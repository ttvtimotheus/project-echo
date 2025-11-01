#!/bin/bash
set -e

echo "=========================================="
echo "Project ECHO - Deploy All Services (v1)"
echo "=========================================="
echo ""

PROJECT_ID="echo-476821"
REGION="europe-west4"
REPO="echo-repo"
TAG="v1"

echo "Step 1: Deploying Analyzer (GPU)..."
gcloud run deploy analyzer \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/analyzer:${TAG} \
  --region=$REGION \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --cpu=4 \
  --memory=16Gi \
  --concurrency=4 \
  --min-instances=0 \
  --max-instances=2 \
  --timeout=300 \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID \
  --no-cpu-throttling \
  --project=$PROJECT_ID

echo ""
echo "Step 2: Deploying Summarizer..."
gcloud run deploy summarizer \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/summarizer:${TAG} \
  --region=$REGION \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --cpu=2 \
  --memory=2Gi \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,GEMINI_API_KEY=${GEMINI_API_KEY} \
  --project=$PROJECT_ID

echo ""
echo "Step 3: Deploying Reporter..."
gcloud run deploy reporter \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/reporter:${TAG} \
  --region=$REGION \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --cpu=1 \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID \
  --project=$PROJECT_ID

echo ""
echo "Step 4: Deploying Dashboard..."
gcloud run deploy dashboard \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/dashboard:${TAG} \
  --region=$REGION \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --cpu=1 \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=5 \
  --project=$PROJECT_ID

echo ""
echo "Step 5: Creating/Updating Crawler Job..."
gcloud run jobs create crawler \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/crawler:${TAG} \
  --region=$REGION \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,MAX_ITEMS=10 \
  --max-retries=3 \
  --task-timeout=10m \
  --project=$PROJECT_ID 2>/dev/null || \
gcloud run jobs update crawler \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/crawler:${TAG} \
  --region=$REGION \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,MAX_ITEMS=10 \
  --project=$PROJECT_ID

echo ""
echo "=========================================="
echo "✓ All services deployed successfully!"
echo "=========================================="
