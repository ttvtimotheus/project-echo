#!/bin/bash
set -e

echo "=========================================="
echo "Project ECHO - Deploy All Services"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Deploy services in order
echo "Step 1: Deploying Analyzer..."
bash "$SCRIPT_DIR/deploy-analyzer.sh"
echo ""

echo "Step 2: Deploying Summarizer..."
bash "$SCRIPT_DIR/deploy-summarizer.sh"
echo ""

echo "Step 3: Deploying Reporter..."
bash "$SCRIPT_DIR/deploy-reporter.sh"
echo ""

echo "Step 4: Deploying Crawler Job..."
bash "$SCRIPT_DIR/deploy-crawler-job.sh"
echo ""

echo "Step 5: Setting up Pub/Sub..."
bash "$SCRIPT_DIR/setup-pubsub.sh"
echo ""

echo "=========================================="
echo "✓ All services deployed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run the crawler:"
echo "   gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821"
echo ""
echo "2. Check logs:"
echo "   gcloud beta logging tail 'resource.type=cloud_run_revision' --project=echo-476821"
echo ""
echo "3. View latest report:"
echo "   REPORTER_URL=\$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')"
echo "   curl -s \$REPORTER_URL/latest"
