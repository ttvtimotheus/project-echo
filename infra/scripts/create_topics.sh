#!/bin/bash
set -e

echo "Creating Pub/Sub topics for Project ECHO..."

PROJECT_ID="echo-476821"

# Create topics
gcloud pubsub topics create echo-ingest --project=$PROJECT_ID || echo "Topic echo-ingest already exists"
gcloud pubsub topics create echo-analyzed --project=$PROJECT_ID || echo "Topic echo-analyzed already exists"
gcloud pubsub topics create echo-summarized --project=$PROJECT_ID || echo "Topic echo-summarized already exists"

echo "✓ Pub/Sub topics created successfully!"
echo ""
echo "Topics:"
echo "  - echo-ingest"
echo "  - echo-analyzed"
echo "  - echo-summarized"
