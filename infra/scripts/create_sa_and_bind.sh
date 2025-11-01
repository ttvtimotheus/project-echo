#!/bin/bash
set -e

echo "Creating service account and binding to Cloud Run services..."

PROJECT_ID="echo-476821"
REGION="europe-west4"
SA_NAME="pubsub-push"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create $SA_NAME \
  --display-name="PubSub Push SA" \
  --project=$PROJECT_ID || echo "Service account already exists"

echo "Service account: $SA_EMAIL"
echo ""

# Bind to Cloud Run services
echo "Binding to analyzer..."
gcloud run services add-iam-policy-binding analyzer \
  --region=$REGION \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

echo "Binding to summarizer..."
gcloud run services add-iam-policy-binding summarizer \
  --region=$REGION \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

echo "Binding to reporter..."
gcloud run services add-iam-policy-binding reporter \
  --region=$REGION \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

echo ""
echo "✓ Service account created and bound to all services!"
