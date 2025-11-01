#!/bin/bash
set -e

echo "=========================================="
echo "Project ECHO - Build All Images"
echo "=========================================="
echo ""

PROJECT_ID="echo-476821"
REGION="europe-west4"
REPO="echo-repo"
TAG="v1"

# Change to project root
cd "$(dirname "$0")/../.."

echo "Building analyzer (GPU-enabled)..."
gcloud builds submit services/analyzer \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/analyzer:${TAG} \
  --project=$PROJECT_ID \
  --timeout=20m

echo ""
echo "Building summarizer..."
gcloud builds submit services/summarizer \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/summarizer:${TAG} \
  --project=$PROJECT_ID

echo ""
echo "Building reporter..."
gcloud builds submit services/reporter \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/reporter:${TAG} \
  --project=$PROJECT_ID

echo ""
echo "Building dashboard..."
gcloud builds submit dashboard \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/dashboard:${TAG} \
  --project=$PROJECT_ID

echo ""
echo "Building crawler job..."
gcloud builds submit services/crawler \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/crawler:${TAG} \
  --project=$PROJECT_ID

echo ""
echo "=========================================="
echo "✓ All images built successfully!"
echo "=========================================="
echo ""
echo "Images:"
echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/analyzer:${TAG}"
echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/summarizer:${TAG}"
echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/reporter:${TAG}"
echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/dashboard:${TAG}"
echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/crawler:${TAG}"
