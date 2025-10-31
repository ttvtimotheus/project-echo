#!/bin/bash
set -e

PROJECT_ID="echo-476821"
REGION="europe-west4"
SA_NAME="pubsub-push"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "Setting up Pub/Sub topics and subscriptions for Project ECHO..."

# Create topics if they don't exist
echo "Creating Pub/Sub topics..."
gcloud pubsub topics create echo-ingest --project=$PROJECT_ID 2>/dev/null || echo "Topic echo-ingest already exists"
gcloud pubsub topics create echo-analyzed --project=$PROJECT_ID 2>/dev/null || echo "Topic echo-analyzed already exists"
gcloud pubsub topics create echo-summarized --project=$PROJECT_ID 2>/dev/null || echo "Topic echo-summarized already exists"

# Create service account for Pub/Sub push
echo "Creating service account for Pub/Sub push..."
gcloud iam service-accounts create $SA_NAME \
  --display-name="PubSub Push Service Account" \
  --project=$PROJECT_ID 2>/dev/null || echo "Service account already exists"

# Get service URLs
echo "Getting Cloud Run service URLs..."
ANALYZER_URL=$(gcloud run services describe analyzer --region=$REGION --project=$PROJECT_ID --format='value(status.url)' 2>/dev/null || echo "")
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=$REGION --project=$PROJECT_ID --format='value(status.url)' 2>/dev/null || echo "")
REPORTER_URL=$(gcloud run services describe reporter --region=$REGION --project=$PROJECT_ID --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$ANALYZER_URL" ] || [ -z "$SUMMARIZER_URL" ] || [ -z "$REPORTER_URL" ]; then
  echo "ERROR: One or more services are not deployed. Please deploy all services first."
  echo "  analyzer: $ANALYZER_URL"
  echo "  summarizer: $SUMMARIZER_URL"
  echo "  reporter: $REPORTER_URL"
  exit 1
fi

# Grant Cloud Run Invoker role to service account
echo "Granting Cloud Run Invoker role to service account..."
gcloud run services add-iam-policy-binding analyzer \
  --region=$REGION \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

gcloud run services add-iam-policy-binding summarizer \
  --region=$REGION \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

gcloud run services add-iam-policy-binding reporter \
  --region=$REGION \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

# Create or update subscriptions
echo "Creating Pub/Sub push subscriptions..."

# Subscription: echo-ingest -> analyzer
gcloud pubsub subscriptions delete sub-analyze --project=$PROJECT_ID 2>/dev/null || true
gcloud pubsub subscriptions create sub-analyze \
  --topic=echo-ingest \
  --push-endpoint="${ANALYZER_URL}/analyze" \
  --push-auth-service-account="$SA_EMAIL" \
  --ack-deadline=60 \
  --project=$PROJECT_ID

# Subscription: echo-analyzed -> summarizer
gcloud pubsub subscriptions delete sub-summarize --project=$PROJECT_ID 2>/dev/null || true
gcloud pubsub subscriptions create sub-summarize \
  --topic=echo-analyzed \
  --push-endpoint="${SUMMARIZER_URL}/summarize" \
  --push-auth-service-account="$SA_EMAIL" \
  --ack-deadline=60 \
  --project=$PROJECT_ID

# Subscription: echo-summarized -> reporter
gcloud pubsub subscriptions delete sub-report --project=$PROJECT_ID 2>/dev/null || true
gcloud pubsub subscriptions create sub-report \
  --topic=echo-summarized \
  --push-endpoint="${REPORTER_URL}/report" \
  --push-auth-service-account="$SA_EMAIL" \
  --ack-deadline=60 \
  --project=$PROJECT_ID

echo ""
echo "✓ Pub/Sub setup complete!"
echo ""
echo "Topics:"
echo "  - echo-ingest"
echo "  - echo-analyzed"
echo "  - echo-summarized"
echo ""
echo "Subscriptions:"
echo "  - sub-analyze: echo-ingest -> $ANALYZER_URL/analyze"
echo "  - sub-summarize: echo-analyzed -> $SUMMARIZER_URL/summarize"
echo "  - sub-report: echo-summarized -> $REPORTER_URL/report"
echo ""
echo "Test the pipeline with:"
echo "gcloud pubsub topics publish echo-ingest --message='{\"doc_id\":\"test-001\",\"link\":\"https://example.com\"}' --project=$PROJECT_ID"
