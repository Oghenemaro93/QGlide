#!/bin/bash

# Cloud SQL Proxy Setup Script
# This script helps you connect to Cloud SQL from your local machine

set -e

PROJECT_ID="your-gcp-project-id"  # Replace with your GCP project ID
INSTANCE_NAME="qglide-db"
REGION="us-central1"

echo "🔌 Setting up Cloud SQL Proxy for local development..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")

echo "📋 Connection Name: $CONNECTION_NAME"

# Download Cloud SQL Proxy
echo "⬇️ Downloading Cloud SQL Proxy..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
else
    echo "❌ Unsupported OS. Please download Cloud SQL Proxy manually."
    exit 1
fi

chmod +x cloud_sql_proxy

echo "✅ Cloud SQL Proxy downloaded successfully!"
echo ""
echo "🔧 Usage Instructions:"
echo ""
echo "1. Start the proxy (in one terminal):"
echo "   ./cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:5432"
echo ""
echo "2. Connect to database (in another terminal):"
echo "   psql -h 127.0.0.1 -p 5432 -U qglide_user -d qglide_prod"
echo ""
echo "3. Update your local .env file:"
echo "   DATABASE_HOST=127.0.0.1"
echo "   DATABASE_PORT=5432"
echo "   DATABASE_NAME=qglide_prod"
echo "   DATABASE_USER=qglide_user"
echo "   DATABASE_PASSWORD=your-password"
echo ""
echo "4. Run Django migrations:"
echo "   python manage.py migrate"
echo ""
echo "5. Create superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "⚠️  Note: Keep the proxy running while developing locally!"
