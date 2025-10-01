# QGlide Cloud SQL Setup Guide

## Quick Setup

### 1. Update Configuration

Edit `setup_cloud_sql.sh` and replace:
- `your-gcp-project-id` with your actual GCP project ID
- `your-secure-password-here` with a strong password

### 2. Run Setup Script

```bash
./setup_cloud_sql.sh
```

This will:
- Create a PostgreSQL instance
- Create database and user
- Set up basic security
- Display connection details

## Manual Setup (Alternative)

### 1. Enable APIs

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com
```

### 2. Create Instance

```bash
gcloud sql instances create qglide-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup \
    --authorized-networks=0.0.0.0/0
```

### 3. Create Database

```bash
gcloud sql databases create qglide_prod --instance=qglide-db
```

### 4. Create User

```bash
gcloud sql users create qglide_user \
    --instance=qglide-db \
    --password=your-secure-password
```

## Local Development with Cloud SQL

### 1. Setup Cloud SQL Proxy

```bash
./cloud_sql_proxy_setup.sh
```

### 2. Start Proxy

```bash
./cloud_sql_proxy -instances=your-project:us-central1:qglide-db=tcp:5432
```

### 3. Update Local Environment

Create `.env.local`:
```bash
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
DATABASE_NAME=qglide_prod
DATABASE_USER=qglide_user
DATABASE_PASSWORD=your-password
ENVIRONMENT=development
```

### 4. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Production Deployment

### 1. Get Instance Details

```bash
# Get IP address
gcloud sql instances describe qglide-db --format="value(ipAddresses[0].ipAddress)"

# Get connection name
gcloud sql instances describe qglide-db --format="value(connectionName)"
```

### 2. Update Environment Variables

Copy `env.production.example` to `.env` and update:

```bash
DATABASE_HOST=your-cloud-sql-ip
DATABASE_NAME=qglide_prod
DATABASE_USER=qglide_user
DATABASE_PASSWORD=your-password
```

### 3. Deploy to Cloud Run

```bash
./deploy.sh
```

## Security Best Practices

### 1. Restrict Network Access

```bash
# Get Cloud Run IP ranges
gcloud run services describe qglide-backend --region=us-central1 --format="value(status.url)"

# Update authorized networks
gcloud sql instances patch qglide-db \
    --authorized-networks=your-cloud-run-ip/32
```

### 2. Enable SSL

```bash
# Download SSL certificate
gcloud sql ssl-certs create client-cert qglide-db

# Update Django settings for SSL
DATABASE_OPTIONS={"sslmode": "require"}
```

### 3. Use Secret Manager

```bash
# Create secrets
gcloud secrets create db-password --data-file=password.txt
gcloud secrets create db-user --data-file=user.txt

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:your-service-account" \
    --role="roles/secretmanager.secretAccessor"
```

## Monitoring and Maintenance

### 1. View Logs

```bash
gcloud sql operations list --instance=qglide-db
```

### 2. Backup

```bash
# Manual backup
gcloud sql backups create --instance=qglide-db

# Automated backups (already enabled)
gcloud sql instances describe qglide-db --format="value(settings.backupConfiguration)"
```

### 3. Performance Monitoring

- Go to [Cloud SQL Console](https://console.cloud.google.com/sql)
- Select your instance
- View metrics, logs, and performance insights

## Troubleshooting

### Common Issues

1. **Connection refused**: Check authorized networks
2. **Authentication failed**: Verify username/password
3. **Database not found**: Ensure database exists
4. **SSL errors**: Check SSL configuration

### Debug Commands

```bash
# Test connection
gcloud sql connect qglide-db --user=qglide_user --database=qglide_prod

# Check instance status
gcloud sql instances describe qglide-db

# View recent operations
gcloud sql operations list --instance=qglide-db --limit=10
```

### Connection Testing

```bash
# Test with psql
psql -h your-cloud-sql-ip -p 5432 -U qglide_user -d qglide_prod

# Test with Django
python manage.py dbshell
```

## Cost Optimization

### Free Tier Limits

- **db-f1-micro**: 1 instance
- **Storage**: 10GB included
- **Backups**: 7 days retention

### Scaling Options

```bash
# Scale up for production
gcloud sql instances patch qglide-db \
    --tier=db-g1-small \
    --storage-size=20GB

# Enable read replicas
gcloud sql instances create qglide-db-replica \
    --master-instance-name=qglide-db \
    --tier=db-f1-micro
```

## Next Steps

1. **Set up monitoring** with Cloud Monitoring
2. **Configure alerts** for disk space and connections
3. **Implement connection pooling** for high traffic
4. **Set up automated backups** and disaster recovery
5. **Monitor costs** and optimize usage

## Support

- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [PostgreSQL on Cloud SQL](https://cloud.google.com/sql/docs/postgres)
- [Django with Cloud SQL](https://cloud.google.com/python/django/cloud-sql)
