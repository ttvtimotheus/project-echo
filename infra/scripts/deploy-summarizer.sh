#!/bin/bash
set -e

PROJECT_ID="echo-476821"
REGION="europe-west4"
SERVICE_NAME="summarizer"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REPO="echo-repo"

echo "Building and deploying $SERVICE_NAME..."

# Build image
echo "Building Docker image..."
gcloud builds submit services/$SERVICE_NAME \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$IMAGE_TAG \
  --project=$PROJECT_ID

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$IMAGE_TAG \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --cpu=1 \
  --memory=512Mi \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID \
  --max-instances=10 \
  --timeout=60 \
  --project=$PROJECT_ID

# Force traffic to latest
echo "Routing traffic to latest revision..."
gcloud run services update-traffic $SERVICE_NAME \
  --region=$REGION \
  --to-latest \
  --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

echo "✓ $SERVICE_NAME deployed successfully!"
echo "URL: $SERVICE_URL"
echo ""
echo "Test with:"
echo "curl -s $SERVICE_URL/"
echo "curl -s $SERVICE_URL/healthz"
