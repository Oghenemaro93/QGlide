# QGlide Backend - Google Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed (for local testing)

## Quick Deployment

### 1. Set up your GCP project

```bash
# Create a new GCP project (or use existing)
gcloud projects create your-project-id --name="QGlide Backend"

# Set the project
gcloud config set project your-project-id

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing
```

### 2. Update deployment script

Edit `deploy.sh` and replace `your-gcp-project-id` with your actual project ID:

```bash
PROJECT_ID="your-actual-project-id"
```

### 3. Deploy to Cloud Run

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## Manual Deployment Steps

### 1. Enable required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build and push Docker image

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/your-project-id/qglide-backend .
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy qglide-backend \
    --image gcr.io/your-project-id/qglide-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production
```

## Environment Variables

Set these environment variables in Cloud Run:

### Required for Production

```bash
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-service-url.run.app

# Database (Cloud SQL)
DATABASE_NAME=qglide_prod
DATABASE_USER=postgres
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=your-cloud-sql-ip
DATABASE_PORT=5432

# CORS
CSRF_TRUSTED_ORIGINS=https://your-service-url.run.app
CSRF_COOKIE_DOMAIN=your-service-url.run.app
SECURE_SSL_REDIRECT=True

# Email (MailerSend)
MAILERSEND_API_KEY=your-mailersend-key
MAILERSEND_DOMAIN=your-domain.com

# SMS (Brevor)
BREVOR_API_KEY=your-brevor-key
```

## Database Setup (Cloud SQL)

### 1. Create Cloud SQL PostgreSQL instance

```bash
gcloud sql instances create qglide-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB
```

### 2. Create database

```bash
gcloud sql databases create qglide_prod --instance=qglide-db
```

### 3. Create user

```bash
gcloud sql users create postgres \
    --instance=qglide-db \
    --password=your-secure-password
```

### 4. Get connection details

```bash
# Get instance IP
gcloud sql instances describe qglide-db --format="value(ipAddresses[0].ipAddress)"
```

## Post-Deployment

### 1. Run migrations

```bash
# Connect to Cloud Run service
gcloud run services proxy qglide-backend --port=8080

# In another terminal, run migrations
gcloud run services update qglide-backend \
    --set-env-vars="RUN_MIGRATIONS=true"
```

### 2. Create superuser

```bash
# Access the service
gcloud run services proxy qglide-backend --port=8080

# Create superuser (in another terminal)
python manage.py createsuperuser
```

## Monitoring and Logs

### View logs

```bash
gcloud run logs tail qglide-backend --region us-central1
```

### Monitor performance

- Go to [Cloud Run Console](https://console.cloud.google.com/run)
- Select your service
- View metrics, logs, and revisions

## Cost Optimization

### Free Tier Limits

- **Cloud Run**: 2 million requests/month
- **Cloud SQL**: 1 instance (db-f1-micro)
- **Container Registry**: 0.5GB storage

### Scaling Configuration

```bash
# Update service with custom scaling
gcloud run services update qglide-backend \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=80 \
    --cpu=1 \
    --memory=1Gi
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile and dependencies
2. **Service won't start**: Check environment variables
3. **Database connection**: Verify Cloud SQL settings
4. **CORS errors**: Update CSRF_TRUSTED_ORIGINS

### Debug Commands

```bash
# Check service status
gcloud run services describe qglide-backend --region us-central1

# View recent logs
gcloud run logs read qglide-backend --region us-central1 --limit=50

# Test locally with Cloud SQL
gcloud sql connect qglide-db --user=postgres
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data
2. **Enable IAM** for service accounts
3. **Set up VPC** for database access
4. **Use HTTPS** only
5. **Regular security updates**

## Next Steps

1. Set up **Cloud SQL** for production database
2. Configure **Custom Domain** with SSL
3. Set up **CI/CD** with Cloud Build
4. Implement **Monitoring** and **Alerting**
5. Set up **Backup** strategies

## Support

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Django on Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-django-service)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
