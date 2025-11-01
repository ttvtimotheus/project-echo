#!/bin/bash
set -e

echo "=========================================="
echo "Project ECHO - Post-Deployment Verification"
echo "=========================================="
echo ""

PROJECT_ID="echo-476821"
REGION="europe-west4"

echo "Step 1: Updating traffic to latest revisions..."
gcloud run services update-traffic analyzer   --region=$REGION --to-latest --project=$PROJECT_ID
gcloud run services update-traffic summarizer --region=$REGION --to-latest --project=$PROJECT_ID
gcloud run services update-traffic reporter   --region=$REGION --to-latest --project=$PROJECT_ID
gcloud run services update-traffic dashboard  --region=$REGION --to-latest --project=$PROJECT_ID

echo ""
echo "Step 2: Fetching service URLs..."
ANALYZER_URL=$(gcloud run services describe analyzer --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
REPORTER_URL=$(gcloud run services describe reporter --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
DASHBOARD_URL=$(gcloud run services describe dashboard --region=$REGION --project=$PROJECT_ID --format='value(status.url)')

echo ""
echo "Step 3: Health check tests..."
echo "Testing Reporter..."
curl -sf ${REPORTER_URL}/healthz && echo "✓ Reporter healthy" || echo "✗ Reporter failed"

echo "Testing Summarizer..."
curl -sf ${SUMMARIZER_URL}/healthz && echo "✓ Summarizer healthy" || echo "✗ Summarizer failed"

echo "Testing Analyzer..."
curl -sf ${ANALYZER_URL}/healthz && echo "✓ Analyzer healthy" || echo "✗ Analyzer failed"

echo ""
echo "=========================================="
echo "✓ Verification complete!"
echo "=========================================="
echo ""
echo "Service URLs:"
echo "  Analyzer:    $ANALYZER_URL"
echo "  Summarizer:  $SUMMARIZER_URL"
echo "  Reporter:    $REPORTER_URL"
echo "  Dashboard:   $DASHBOARD_URL"
echo ""
echo "Test the pipeline:"
echo "  gcloud pubsub topics publish echo-ingest --message='{\"doc_id\":\"test-001\",\"title\":\"Test\",\"link\":\"https://example.com\"}' --project=$PROJECT_ID"
echo ""
echo "View latest report:"
echo "  curl -s ${REPORTER_URL}/latest | jq '.html' -r"
echo ""
echo "Open dashboard:"
echo "  open $DASHBOARD_URL"
