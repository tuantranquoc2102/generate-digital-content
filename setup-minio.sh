#!/bin/bash
# MinIO setup script

echo "Setting up MinIO bucket..."

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until curl -f http://localhost:9000/minio/health/ready; do
  echo "Waiting for MinIO..."
  sleep 2
done

echo "MinIO is ready, creating bucket..."

# Install mc (MinIO client) if not exists
if ! command -v mc &> /dev/null; then
    echo "Installing MinIO client..."
    curl -O https://dl.min.io/client/mc/release/darwin-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
fi

# Configure mc
mc alias set local http://localhost:9000 minio minio123

# Create bucket
mc mb local/uploads

# Set bucket policy for public read
mc anonymous set public local/uploads

# Set CORS policy
echo '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedOrigins": ["http://localhost:3000"],
      "ExposeHeaders": []
    }
  ]
}' > cors.json

mc admin config set local cors_config < cors.json
mc admin service restart local

echo "MinIO bucket setup completed!"