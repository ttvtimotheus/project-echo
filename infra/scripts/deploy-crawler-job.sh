#!/bin/bash
set -e

PROJECT_ID="echo-476821"
REGION="europe-west4"
JOB_NAME="crawler"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REPO="echo-repo"

echo "Building and deploying $JOB_NAME job..."

# Build image
echo "Building Docker image..."
gcloud builds submit services/crawler \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$JOB_NAME:$IMAGE_TAG \
  --project=$PROJECT_ID

# Create or update Cloud Run Job
echo "Creating/updating Cloud Run Job..."
gcloud run jobs deploy $JOB_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$JOB_NAME:$IMAGE_TAG \
  --region=$REGION \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID \
  --max-retries=3 \
  --task-timeout=10m \
  --project=$PROJECT_ID \
  --execute-now=false

echo "✓ $JOB_NAME job deployed successfully!"
echo ""
echo "Run the job with:"
echo "gcloud run jobs execute $JOB_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "Monitor execution:"
echo "gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --project=$PROJECT_ID"
