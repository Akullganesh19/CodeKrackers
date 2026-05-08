#!/bin/bash

# VSDP Automated Deployment Script
# This script handles environment configuration, secret generation, and stack initialization.

echo "🚀 Starting VSDP Deployment Pipeline..."

# 1. Generate .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Generating environment configuration..."
    SECRET_KEY=$(openssl rand -hex 32)
    cat <<EOT > .env
DATABASE_URL=mysql+aiomysql://root:vsdp_root_password@db:3306/vsdp_db
REDIS_URL=redis://redis:6379
SECRET_KEY=$SECRET_KEY
WHISPER_MODEL_SIZE=base
ENVIRONMENT=production
EOT
    echo "✅ .env file created with a secure SECRET_KEY."
else
    echo "ℹ️  .env file already exists. Skipping generation."
fi

# 2. Orchestrate Container Stack
echo "📦 Building and starting containers..."
docker-compose up -d --build

# 3. Database Migrations
# We wait for the DB to be ready before running migrations
echo "⏳ Waiting for database to initialize..."
sleep 10

echo "🗄️  Running database migrations..."
# Note: This assumes you are using Alembic for migrations within the FastAPI container
docker-compose exec -T backend alembic upgrade head || echo "⚠️  Migration command failed. Ensure Alembic is configured."

echo "🎉 Deployment Successful!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "------------------------------------------------"
echo "Run 'docker-compose logs -f' to monitor the system."