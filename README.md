# Project ECHO

> "In a world drowning in information, the future belongs to systems that can think for themselves." :)

An autonomous, serverless AI research pipeline on Google Cloud Run that crawls, analyzes, summarizes, and reports on research papers from ArXiv.

## Quick Start

Deploy the entire system with one command:

```bash
cd infra/scripts
chmod +x *.sh
./deploy-all.sh
```

Run the crawler to process papers:

```bash
gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821
```

View the latest report:

```bash
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/latest | jq -r '.html'
```

## Architecture

Project ECHO follows an event-driven microservices architecture:

```
ArXiv RSS → Crawler → echo-ingest → Analyzer (GPU) → echo-analyzed → 
Summarizer → echo-summarized → Reporter → HTML Reports
```

All services communicate via Google Cloud Pub/Sub and store data in Firestore.

See [docs/arch.md](docs/arch.md) for detailed architecture documentation.

## Services

### 1. Crawler (Cloud Run Job)
Fetches ArXiv CS papers and publishes to the ingestion pipeline.

**Deploy:**
```bash
cd infra/scripts
./deploy-crawler-job.sh
```

**Run:**
```bash
gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821
```

### 2. Analyzer (Cloud Run Service + NVIDIA L4 GPU)
Analyzes documents and extracts topics using GPU acceleration.

**Deploy:**
```bash
./deploy-analyzer.sh
```

**Test:**
```bash
ANALYZER_URL=$(gcloud run services describe analyzer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $ANALYZER_URL/healthz
```

### 3. Summarizer (Cloud Run Service)
Generates summaries from analyzed documents.

**Deploy:**
```bash
./deploy-summarizer.sh
```

**Test:**
```bash
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $SUMMARIZER_URL/healthz
```

### 4. Reporter (Cloud Run Service)
Aggregates summaries into HTML reports.

**Deploy:**
```bash
./deploy-reporter.sh
```

**Test:**
```bash
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/
curl -s $REPORTER_URL/healthz
curl -s $REPORTER_URL/latest
```

## Infrastructure Setup

### Prerequisites

1. **GCP Project**: `echo-476821`
2. **Region**: `europe-west4`
3. **Artifact Registry**: Repository named `echo-repo` must exist
4. **APIs Enabled**:
   - Cloud Run
   - Cloud Build
   - Pub/Sub
   - Firestore
   - Artifact Registry

5. **gcloud CLI** installed and authenticated:
```bash
gcloud auth login
gcloud config set project echo-476821
```

### Pub/Sub Setup

Create topics and subscriptions with OIDC authentication:

```bash
cd infra/scripts
./setup-pubsub.sh
```

This script:
- Creates Pub/Sub topics (`echo-ingest`, `echo-analyzed`, `echo-summarized`)
- Creates service account (`pubsub-push`)
- Grants Cloud Run Invoker role
- Creates push subscriptions with OIDC auth

## End-to-End Testing

### 1. Test Individual Services

```bash
# Test Reporter
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/ | jq
# Expected: {"service":"reporter","ok":true}

# Test Summarizer
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $SUMMARIZER_URL/ | jq
# Expected: {"service":"summarizer","ok":true}

# Test Analyzer
ANALYZER_URL=$(gcloud run services describe analyzer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $ANALYZER_URL/ | jq
# Expected: {"service":"analyzer","ok":true}
```

### 2. Test Pub/Sub Pipeline

Publish a test message to trigger the entire pipeline:

```bash
gcloud pubsub topics publish echo-ingest \
  --message='{"doc_id":"test-001","link":"https://example.com"}' \
  --project=echo-476821
```

### 3. Monitor Logs

Watch logs for all services:

```bash
gcloud beta logging tail \
  'resource.type=cloud_run_revision AND (resource.labels.service_name=analyzer OR resource.labels.service_name=summarizer OR resource.labels.service_name=reporter)' \
  --project=echo-476821
```

### 4. Run Complete Flow

```bash
# Run crawler to ingest papers
gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821

# Wait 2-3 minutes for pipeline to process

# Check latest report
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/latest | jq -r '.html' > report.html
open report.html  # or cat report.html
```

## Project Structure

```
project-echo/
├── services/
│   ├── analyzer/          # Document analysis service (GPU)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── summarizer/        # Summary generation service
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── reporter/          # Report aggregation service
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── crawler/           # ArXiv crawler job
│       ├── main.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .dockerignore
├── infra/
│   └── scripts/           # Deployment automation
│       ├── deploy-all.sh
│       ├── deploy-analyzer.sh
│       ├── deploy-summarizer.sh
│       ├── deploy-reporter.sh
│       ├── deploy-crawler-job.sh
│       └── setup-pubsub.sh
├── docs/
│   └── arch.md           # Architecture documentation
├── dashboard/            # Future: Next.js frontend
├── .gitignore
└── README.md
```

## Service Endpoints

| Service | Base URL | Health Check | Main Endpoint |
|---------|----------|--------------|---------------|
| Analyzer | `https://analyzer-*.run.app` | `GET /healthz` | `POST /analyze` |
| Summarizer | `https://summarizer-*.run.app` | `GET /healthz` | `POST /summarize` |
| Reporter | `https://reporter-*.run.app` | `GET /healthz` | `GET /latest` |

## Environment Variables

All services use:
- `PORT`: Provided by Cloud Run (8080 default)
- `GCP_PROJECT`: Set to `echo-476821`

## Troubleshooting

### Service returns 404

Check that routes are registered:
```bash
gcloud beta logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=reporter' --project=echo-476821 | grep "Registered routes"
```

### Pub/Sub messages not processing

Verify subscriptions exist and are healthy:
```bash
gcloud pubsub subscriptions list --project=echo-476821
gcloud pubsub subscriptions describe sub-analyze --project=echo-476821
```

### Firestore permission errors

Ensure Cloud Run service accounts have Firestore permissions:
```bash
gcloud projects get-iam-policy echo-476821 | grep cloud-run
```

### Cold start issues

Services use lazy initialization to avoid cold start crashes. Check logs for "Initializing Firestore client" messages.

## Development

### Local Testing

Run services locally:

```bash
cd services/reporter
export GCP_PROJECT=echo-476821
export PORT=8080
python main.py
```

Test endpoints:
```bash
curl http://localhost:8080/
curl http://localhost:8080/healthz
```

### Build Docker Images Locally

```bash
cd services/reporter
docker build -t reporter:test .
docker run -p 8080:8080 -e GCP_PROJECT=echo-476821 reporter:test
```

## Monitoring

### View Service Metrics

```bash
# Get service details
gcloud run services describe reporter --region=europe-west4 --project=echo-476821

# View recent logs
gcloud beta logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=reporter' --project=echo-476821
```

### Check Firestore Documents

```bash
# Install firebase CLI
npm install -g firebase-tools
firebase login

# Query collections
firebase firestore:get documents --project=echo-476821
firebase firestore:get analyses --project=echo-476821
firebase firestore:get summaries --project=echo-476821
firebase firestore:get reports --project=echo-476821
```

## Cost Optimization

- Services scale to zero when not in use
- Analyzer uses GPU only during processing
- Free tier covers development usage
- Estimated monthly cost: $10-30 for moderate usage

## Roadmap

- [x] Crawler job for ArXiv ingestion
- [x] GPU-based analyzer service
- [x] Summarizer service
- [x] Reporter with HTML generation
- [x] Pub/Sub event-driven architecture
- [ ] Next.js dashboard frontend
- [ ] Cloud Scheduler for automatic runs
- [ ] Advanced ML models for analysis
- [ ] Multi-source support (beyond ArXiv)
- [ ] Email/Slack notifications
- [ ] Custom topic filters

## Contributing

1. Make changes in a feature branch
2. Test locally with sample data
3. Deploy to dev environment
4. Verify end-to-end flow
5. Submit PR with clear description

## License

MIT

## Contact

Project ECHO - Autonomous AI Research Pipeline
