#!/bin/bash

# QGlide Backend Deployment Script for Google Cloud Run
# Make sure you have $GCLOUD_CMD CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="qglide-472613"  # Replace with your GCP project ID
SERVICE_NAME="qglide-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting QGlide Backend deployment to Cloud Run..."

# Use local gcloud installation
GCLOUD_CMD="./google-cloud-sdk/bin/gcloud"

# Check if local gcloud is available
if [ ! -f "$GCLOUD_CMD" ]; then
    echo "❌ Local gcloud CLI not found at $GCLOUD_CMD"
    echo "Available files:"
    ls -la google-cloud-sdk/bin/ | head -10
    exit 1
fi

# Check if user is authenticated
if ! $GCLOUD_CMD auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run '$GCLOUD_CMD auth login' first."
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
$GCLOUD_CMD config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
$GCLOUD_CMD services enable cloudbuild.googleapis.com
$GCLOUD_CMD services enable run.googleapis.com
$GCLOUD_CMD services enable containerregistry.googleapis.com

# Build and push the image
echo "🏗️ Building and pushing Docker image..."
$GCLOUD_CMD builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
$GCLOUD_CMD run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production,DATABASE_NAME=qglide_prod,DATABASE_USER=qglide_user,DATABASE_PASSWORD=QGlide2024!Secure,DATABASE_HOST=136.115.154.205,DATABASE_PORT=5432,SECRET_KEY=django-insecure-temp-key-please-change,MAILERSEND_API_KEY=,MAILERSEND_DOMAIN=,BREVOR_API_KEY=,EMAIL_HOST_USER=your-email@gmail.com,EMAIL_HOST_PASSWORD=your-gmail-app-password,DEFAULT_FROM_EMAIL=noreply@qglide.com,FIREBASE_CREDENTIALS_PATH=/app/firebase-service-account.json,FIREBASE_PROJECT_ID=qglide-firebase \
    --add-cloudsql-instances qglide-472613:us-central1:qglide-db

# Get the service URL
SERVICE_URL=$($GCLOUD_CMD run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 API Documentation: $SERVICE_URL/"
echo "🔧 Admin Panel: $SERVICE_URL/admin/"

# Display useful commands
echo ""
echo "📝 Useful commands:"
echo "  View logs: $GCLOUD_CMD run logs tail $SERVICE_NAME --region $REGION"
echo "  Update service: $GCLOUD_CMD run services update $SERVICE_NAME --region $REGION"
echo "  Delete service: $GCLOUD_CMD run services delete $SERVICE_NAME --region $REGION"
