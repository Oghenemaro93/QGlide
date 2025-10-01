#!/bin/bash

# QGlide Cloud SQL Setup Script
# This script sets up a PostgreSQL instance on Google Cloud SQL

set -e

# Configuration
PROJECT_ID="qglide-472613"  # Replace with your GCP project ID
INSTANCE_NAME="qglide-db"
DATABASE_NAME="qglide_prod"
DB_USER="qglide_user"
DB_PASSWORD="QGlide2024!Secure"  # Replace with a secure password
REGION="us-central1"
TIER="db-f1-micro"  # Free tier instance

echo "🗄️ Setting up Cloud SQL PostgreSQL for QGlide..."

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
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com

# Create Cloud SQL instance
echo "🏗️ Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_14 \
    --tier=$TIER \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup \
    --authorized-networks=0.0.0.0/0

# Wait for instance to be ready
echo "⏳ Waiting for instance to be ready..."
gcloud sql instances describe $INSTANCE_NAME --format="value(state)" | grep -q RUNNABLE || {
    echo "⏳ Instance is still starting, waiting..."
    sleep 30
}

# Set root password
echo "🔐 Setting root password..."
gcloud sql users set-password postgres \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create database
echo "📊 Creating database..."
gcloud sql databases create $DATABASE_NAME --instance=$INSTANCE_NAME

# Create application user
echo "👤 Creating application user..."
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

# Get instance connection details
echo "📋 Getting connection details..."
INSTANCE_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")

echo "✅ Cloud SQL setup completed successfully!"
echo ""
echo "📊 Database Details:"
echo "  Instance Name: $INSTANCE_NAME"
echo "  Database Name: $DATABASE_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  IP Address: $INSTANCE_IP"
echo "  Connection Name: $CONNECTION_NAME"
echo ""
echo "🔗 Connection String:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@$INSTANCE_IP:5432/$DATABASE_NAME"
echo ""
echo "📝 Environment Variables for Cloud Run:"
echo "  DATABASE_NAME=$DATABASE_NAME"
echo "  DATABASE_USER=$DB_USER"
echo "  DATABASE_PASSWORD=$DB_PASSWORD"
echo "  DATABASE_HOST=$INSTANCE_IP"
echo "  DATABASE_PORT=5432"
echo ""
echo "🔧 Next Steps:"
echo "  1. Update your .env file with these database credentials"
echo "  2. Test connection: gcloud sql connect $INSTANCE_NAME --user=$DB_USER --database=$DATABASE_NAME"
echo "  3. Run migrations: python manage.py migrate"
echo "  4. Deploy to Cloud Run with these environment variables"
echo ""
echo "⚠️  Security Notes:"
echo "  - Change the default password in production"
echo "  - Restrict authorized networks to your Cloud Run IPs"
echo "  - Enable SSL connections"
echo "  - Set up regular backups"
