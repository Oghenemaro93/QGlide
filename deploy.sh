#!/bin/bash

# QGlide Backend Deployment Script for Google Cloud Run
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="qglide-472613"  # Replace with your GCP project ID
SERVICE_NAME="qglide-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting QGlide Backend deployment to Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the image
echo "🏗️ Building and pushing Docker image..."
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production,DATABASE_NAME=qglide_prod,DATABASE_USER=qglide_user,DATABASE_PASSWORD=QGlide2024!Secure,DATABASE_HOST=136.115.154.205,DATABASE_PORT=5432 \
    --add-cloudsql-instances qglide-472613:us-central1:qglide-db

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 API Documentation: $SERVICE_URL/"
echo "🔧 Admin Panel: $SERVICE_URL/admin/"

# Display useful commands
echo ""
echo "📝 Useful commands:"
echo "  View logs: gcloud run logs tail $SERVICE_NAME --region $REGION"
echo "  Update service: gcloud run services update $SERVICE_NAME --region $REGION"
echo "  Delete service: gcloud run services delete $SERVICE_NAME --region $REGION"
