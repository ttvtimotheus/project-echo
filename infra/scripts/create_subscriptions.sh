#!/bin/bash
set -e

echo "Creating Pub/Sub push subscriptions with OIDC authentication..."

PROJECT_ID="echo-476821"
REGION="europe-west4"
SA_EMAIL="pubsub-push@${PROJECT_ID}.iam.gserviceaccount.com"

# Get service URLs
echo "Fetching Cloud Run service URLs..."
ANALYZER_URL=$(gcloud run services describe analyzer --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
REPORTER_URL=$(gcloud run services describe reporter --region=$REGION --project=$PROJECT_ID --format='value(status.url)')

echo "Analyzer URL: $ANALYZER_URL"
echo "Summarizer URL: $SUMMARIZER_URL"
echo "Reporter URL: $REPORTER_URL"
echo ""

# Create subscriptions with OIDC push
echo "Creating sub-analyze..."
gcloud pubsub subscriptions create sub-analyze \
  --topic=echo-ingest \
  --push-endpoint="${ANALYZER_URL}/analyze" \
  --push-auth-service-account="$SA_EMAIL" \
  --project=$PROJECT_ID || echo "Subscription sub-analyze already exists"

echo "Creating sub-summarize..."
gcloud pubsub subscriptions create sub-summarize \
  --topic=echo-analyzed \
  --push-endpoint="${SUMMARIZER_URL}/summarize" \
  --push-auth-service-account="$SA_EMAIL" \
  --project=$PROJECT_ID || echo "Subscription sub-summarize already exists"

echo "Creating sub-report..."
gcloud pubsub subscriptions create sub-report \
  --topic=echo-summarized \
  --push-endpoint="${REPORTER_URL}/report" \
  --push-auth-service-account="$SA_EMAIL" \
  --project=$PROJECT_ID || echo "Subscription sub-report already exists"

echo ""
echo "✓ Pub/Sub push subscriptions created with OIDC!"
echo ""
echo "Subscriptions:"
echo "  - sub-analyze: echo-ingest -> ${ANALYZER_URL}/analyze"
echo "  - sub-summarize: echo-analyzed -> ${SUMMARIZER_URL}/summarize"
echo "  - sub-report: echo-summarized -> ${REPORTER_URL}/report"
