# Project ECHO - Deployment Guide

## 🚀 Quick Deploy (One Command)

```bash
cd infra/scripts
chmod +x *.sh
./deploy-all.sh
```

This will:
1. Deploy analyzer service with GPU
2. Deploy summarizer service
3. Deploy reporter service (v3)
4. Deploy crawler job
5. Setup Pub/Sub topics and subscriptions with OIDC

**Time**: ~10-15 minutes

---

## 📋 Prerequisites Checklist

Before deploying, ensure:

- [ ] gcloud CLI installed and authenticated
- [ ] Project set: `gcloud config set project echo-476821`
- [ ] Artifact Registry repo `echo-repo` exists in `europe-west4`
- [ ] APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Pub/Sub API
  - Firestore API
  - Artifact Registry API

### Enable APIs (if needed):

```bash
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  artifactregistry.googleapis.com \
  --project=echo-476821
```

### Create Artifact Registry (if needed):

```bash
gcloud artifacts repositories create echo-repo \
  --repository-format=docker \
  --location=europe-west4 \
  --project=echo-476821
```

---

## 🧪 Test Deployment

### 1. Verify Services Are Running

```bash
# Test all services
make test

# Or manually:
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/
# Expected: {"service":"reporter","ok":true}

curl -s $REPORTER_URL/healthz
# Expected: {"ok":true}
```

### 2. Run End-to-End Test

```bash
# Execute crawler
make run-crawler

# Wait 2-3 minutes for pipeline to process

# View report
make view-report
```

### 3. Monitor Logs

```bash
# Tail all service logs
make logs

# Or specific service:
gcloud beta logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=reporter' --project=echo-476821
```

---

## 🔧 Manual Deployment Steps

If you prefer step-by-step deployment:

### Step 1: Deploy Reporter (Fix 404 Issues)

```bash
cd infra/scripts
./deploy-reporter.sh
```

**Test:**
```bash
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/
curl -s $REPORTER_URL/healthz
```

### Step 2: Deploy Summarizer

```bash
./deploy-summarizer.sh
```

**Test:**
```bash
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $SUMMARIZER_URL/
```

### Step 3: Deploy Analyzer

```bash
./deploy-analyzer.sh
```

**Note:** This deploys with NVIDIA L4 GPU and may take longer.

**Test:**
```bash
ANALYZER_URL=$(gcloud run services describe analyzer --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $ANALYZER_URL/
```

### Step 4: Deploy Crawler Job

```bash
./deploy-crawler-job.sh
```

### Step 5: Setup Pub/Sub

```bash
./setup-pubsub.sh
```

This creates:
- Topics: `echo-ingest`, `echo-analyzed`, `echo-summarized`
- Service account: `pubsub-push@echo-476821.iam.gserviceaccount.com`
- Subscriptions with OIDC authentication

---

## 🎯 Acceptance Criteria Verification

### 1. Reporter Base URL Returns JSON (Not 404)

```bash
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --project=echo-476821 --format='value(status.url)')
curl -s $REPORTER_URL/

# Expected:
# {"service":"reporter","ok":true}
# NOT a Google 404 page
```

✅ **PASS** if you see JSON response

### 2. Pub/Sub Push Triggers End-to-End Flow

```bash
# Publish test message
gcloud pubsub topics publish echo-ingest \
  --message='{"doc_id":"test-001","link":"https://example.com"}' \
  --project=echo-476821

# Monitor logs (in separate terminal)
make logs

# Should see:
# - Analyzer: "Analyze endpoint called"
# - Summarizer: "Summarize endpoint called"
# - Reporter: "Report endpoint called"
```

✅ **PASS** if all three services process the message

### 3. Crawler Job Produces Reports

```bash
# Run crawler
gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821

# Wait 2-3 minutes

# Check report
curl -s $REPORTER_URL/latest | jq -r '.html'

# Expected:
# <h1>Daily ECHO</h1><ul><li>Paper title. Topic: machine learning.</li>...</ul>
```

✅ **PASS** if HTML contains list items with paper summaries

### 4. Logs Show Traffic and Document Counts

```bash
# Check logs for document processing
gcloud beta logging tail 'resource.type=cloud_run_revision' --project=echo-476821 --limit=50

# Look for:
# - "Document created: <doc_id>"
# - "Analysis created for doc_id: <doc_id>"
# - "Summary created for doc_id: <doc_id>"
# - "Report generated with X summaries"
```

✅ **PASS** if logs show complete pipeline execution

---

## 🐛 Troubleshooting

### Reporter Returns 404

**Symptoms:** `curl` returns Google's 404 page instead of JSON

**Fix:**
1. Check logs for startup issues:
   ```bash
   gcloud beta logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=reporter' --project=echo-476821
   ```

2. Look for "Registered routes" in logs
3. Redeploy with latest code:
   ```bash
   ./deploy-reporter.sh
   ```

### Pub/Sub Messages Not Processing

**Symptoms:** Messages published but services don't receive them

**Diagnosis:**
```bash
# Check subscriptions exist
gcloud pubsub subscriptions list --project=echo-476821

# Check subscription details
gcloud pubsub subscriptions describe sub-analyze --project=echo-476821

# Check delivery attempts
gcloud pubsub subscriptions pull sub-analyze --limit=5 --project=echo-476821
```

**Fix:**
```bash
# Recreate subscriptions
./setup-pubsub.sh
```

### Cold Start Crashes

**Symptoms:** Services crash immediately after deployment

**Diagnosis:**
```bash
# Check for initialization errors
gcloud beta logging tail 'resource.type=cloud_run_revision AND severity>=ERROR' --project=echo-476821
```

**Fix:**
- Lazy initialization is already implemented
- Check Firestore/Pub/Sub permissions
- Verify GCP_PROJECT environment variable is set

### Firestore Permission Errors

**Symptoms:** "Permission denied" errors in logs

**Fix:**
```bash
# Grant Firestore permissions to Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe echo-476821 --format='value(projectNumber)')
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding echo-476821 \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user"
```

---

## 📊 Monitoring Commands

```bash
# Service status
gcloud run services list --region=europe-west4 --project=echo-476821

# Recent logs
gcloud beta logging tail 'resource.type=cloud_run_revision' --project=echo-476821

# Job executions
gcloud run jobs executions list --job=crawler --region=europe-west4 --project=echo-476821

# Pub/Sub metrics
gcloud pubsub topics list --project=echo-476821
gcloud pubsub subscriptions list --project=echo-476821
```

---

## 🔄 Redeployment

After code changes:

```bash
# Redeploy specific service
./deploy-reporter.sh

# Or redeploy all
./deploy-all.sh
```

**Note:** Subscriptions persist across redeployments. Only re-run `setup-pubsub.sh` if you need to recreate them.

---

## ✅ Success Checklist

- [ ] All services return JSON at base URL (not 404)
- [ ] Health checks pass for all services
- [ ] Pub/Sub topics created
- [ ] Pub/Sub subscriptions created with OIDC
- [ ] Crawler job executes successfully
- [ ] End-to-end flow processes messages
- [ ] Firestore collections populated
- [ ] Latest report accessible via `/latest` endpoint
- [ ] Logs show complete pipeline execution

---

## 🎉 You're Done!

Project ECHO is now running end-to-end on Cloud Run!

**View your report:**
```bash
make view-report
```

**Run another batch:**
```bash
make run-crawler
```

**Monitor the system:**
```bash
make logs
```
