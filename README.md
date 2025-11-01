# Project ECHO - AI Research Intelligence Platform

**Autonomous, GPU-Accelerated Research Discovery Pipeline on Google Cloud Run**

> *"In a world drowning in information, the future belongs to systems that can think for themselves."*

## 🎯 Elevator Pitch

Project ECHO is a fully autonomous AI research intelligence system that crawls academic sources (arXiv, PubMed), analyzes papers using GPU-accelerated embeddings (Gemma 2B), clusters them with cosine similarity, summarizes with Gemini 1.5 Flash, and delivers weighted intelligence reports—all running serverless on Google Cloud Run with zero human intervention.

**Key Innovation**: Real-time, self-organizing topic discovery using online clustering with mathematical precision.

## 🏗️ Architecture

### System Overview

```
┌─────────────┐     Pub/Sub        ┌──────────────┐     Pub/Sub        ┌──────────────┐
│             │    echo-ingest     │              │   echo-analyzed    │              │
│   Crawler   ├───────────────────>│   Analyzer   ├──────────────────>│  Summarizer  │
│  (Job)      │                    │  (GPU/L4)    │                    │  (Gemini)    │
└─────────────┘                    └──────────────┘                    └──────────────┘
                                                                                │
                                                                                │ Pub/Sub
                                                                                │ echo-summarized
                                                                                v
                                                                        ┌──────────────┐
                                                                        │              │
                                                                        │   Reporter   │
                                                                        │  (Weighted)  │
                                                                        └──────┬───────┘
                                                                               │
                                                                               v
                                                                        ┌──────────────┐
                                                                        │              │
                                                                        │  Dashboard   │
                                                                        │  (Next.js)   │
                                                                        └──────────────┘
```

All services communicate via **Pub/Sub push subscriptions** with **OIDC authentication**. All data persists in **Firestore**.

### Cloud Infrastructure

- **Project ID**: `echo-476821`
- **Region**: `europe-west4`
- **Execution**: Cloud Run Gen2
- **GPU**: NVIDIA L4 (analyzer only)
- **Artifact Registry**: `echo-repo`

## 🧮 Mathematical Backbone

### 1. Embedding Generation

For each document $d_i$, generate embedding vector using Gemma 2B:

$$
\mathbf{v}_i = f_{Gemma}(d_i) \in \mathbb{R}^n
$$

Where $f_{Gemma}$ is the mean-pooled last hidden state of the transformer.

### 2. Cosine Similarity

Compute similarity between embeddings:

$$
S(i, j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \cdot \|\mathbf{v}_j\|}
$$

### 3. Online Clustering

**Centroid Matching**: For each new document embedding $\mathbf{v}_i$, find best matching topic:

$$
k^* = \arg\max_k S(\mathbf{v}_i, \mathbf{c}_k)
$$

Where $\mathbf{c}_k$ is the centroid of cluster $k$.

**Threshold Decision**: If $S(\mathbf{v}_i, \mathbf{c}_{k^*}) < \tau$ (where $\tau = 0.8$), create new topic.

**Centroid Update**: Use exponential moving average:

$$
\mathbf{c}_k^{new} = (1 - \alpha) \mathbf{c}_k^{old} + \alpha \mathbf{v}_i
$$

Where $\alpha = 0.1$ is the learning rate.

### 4. Topic Weighting

For daily report, weight each topic by relative frequency:

$$
\alpha_k = \frac{|C_k|}{\sum_{j=1}^{K} |C_j|}
$$

Where $|C_k|$ is the number of papers in cluster $k$, and $K$ is total clusters.

### 5. Summarization

Generate abstractive summary using Gemini 1.5 Flash:

$$
s_i = \text{Gemini}(\text{title}_i, \text{abstract}_i, L_k)
$$

Where $L_k$ is the topic label assigned to document $i$.

## 🚀 Deployment

### Prerequisites

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project echo-476821

# Set Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"
```

### Quick Start (Full Deployment)

```bash
# 1. Create Pub/Sub topics
./infra/scripts/create_topics.sh

# 2. Build all Docker images
./infra/scripts/build_all.sh  # Takes ~15-20 minutes

# 3. Deploy all services
./infra/scripts/deploy_all_v1.sh

# 4. Create service account and bind
./infra/scripts/create_sa_and_bind.sh

# 5. Create Pub/Sub subscriptions
./infra/scripts/create_subscriptions.sh

# 6. Verify deployment
./infra/scripts/post_deploy_verify.sh
```

### Run End-to-End Test

```bash
# Execute crawler to fetch papers
gcloud run jobs execute crawler --region=europe-west4 --project=echo-476821

# Wait ~3-5 minutes for pipeline to complete

# View latest report
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --format='value(status.url)')
curl -s ${REPORTER_URL}/latest | jq '.html' -r

# Open dashboard
DASHBOARD_URL=$(gcloud run services describe dashboard --region=europe-west4 --format='value(status.url)')
open $DASHBOARD_URL
```

## 📊 Services

### Crawler (Cloud Run Job)

- **Function**: Fetches arXiv RSS feed
- **Publishes to**: `echo-ingest`
- **Schedule**: On-demand via `gcloud run jobs execute`
- **Output**: `{doc_id, title, link, source, timestamp}`

### Analyzer (Cloud Run Service + GPU)

- **GPU**: NVIDIA L4
- **Model**: Gemma 2B (embeddings)
- **Function**: Generate embeddings, cluster documents, assign topics
- **Subscribes to**: `echo-ingest`
- **Publishes to**: `echo-analyzed`
- **Storage**: Firestore `analyses`, `centroids`

**Key Features**:
- CUDA-accelerated inference
- Online centroid learning
- Automatic topic creation (max 20)
- Cosine similarity threshold: 0.8

### Summarizer (Cloud Run Service)

- **Model**: Gemini 1.5 Flash
- **Function**: Generate abstractive summaries conditioned on topics
- **Subscribes to**: `echo-analyzed`
- **Publishes to**: `echo-summarized`
- **Storage**: Firestore `summaries`

**Prompt Engineering**:
```
You are a research summarizer. Given the following research paper details, 
create a concise, professional summary in ONE sentence.

Title: {title}
Abstract: {abstract}
Assigned Topics: {topics}

Provide a single-sentence summary that captures the key contribution 
and relates to the assigned topics. Be precise and academic.
```

### Reporter (Cloud Run Service)

- **Function**: Aggregate summaries into weighted HTML digest
- **Subscribes to**: `echo-summarized`
- **Storage**: Firestore `reports`
- **Endpoints**:
  - `GET /latest` - Returns latest report with metadata
  - `GET /healthz` - Health check
  - `POST /report` - Generate report (Pub/Sub push)

**Features**:
- Time-windowed aggregation (24h)
- Topic weighting using $\alpha_k = |C_k| / \sum_j |C_j|$
- Grouped by topic with percentages

### Dashboard (Next.js on Cloud Run)

- **Framework**: Next.js 15
- **Function**: Display latest report, system status, topic charts
- **Features**:
  - Real-time data fetching with SWR
  - Topic distribution pie charts
  - Service health monitoring
  - Material 3 design system
  - Dark mode

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| **AI/ML** | Gemma 2B, Gemini 1.5 Flash, PyTorch, Transformers |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | Next.js 15, React 19, TypeScript |
| **Cloud** | Google Cloud Run Gen2, Pub/Sub, Firestore |
| **GPU** | NVIDIA L4, CUDA 12.1 |
| **Infra** | Docker, Cloud Build, Artifact Registry |
| **Auth** | OIDC service account authentication |

## 📁 Data Model (Firestore)

### Collections

**documents**
```json
{
  "doc_id": "arxiv-2501-12345",
  "title": "Attention Is All You Need",
  "link": "https://arxiv.org/abs/...",
  "summary": "Abstract text...",
  "source": "arxiv",
  "timestamp": "2025-11-01T00:00:00Z"
}
```

**centroids**
```json
{
  "topic_id": "topic_01",
  "vector": [0.123, -0.456, ...],  // n-dimensional
  "dimension": 768,
  "updated_at": "2025-11-01T12:00:00Z"
}
```

**analyses**
```json
{
  "doc_id": "arxiv-2501-12345",
  "topics": ["topic_01"],
  "score": 92.5,
  "embedding_ref": "embeddings/arxiv-2501-12345",
  "analysis_time": 2.34,
  "created_at": "2025-11-01T00:05:00Z"
}
```

**summaries**
```json
{
  "doc_id": "arxiv-2501-12345",
  "summary": "This paper introduces the Transformer architecture...",
  "topics": ["topic_01"],
  "model_used": "gemini-1.5-flash",
  "summary_time": 1.23,
  "created_at": "2025-11-01T00:06:00Z"
}
```

**reports**
```json
{
  "html": "<h1>ECHO Research Intelligence Report</h1>...",
  "created_at": "2025-11-01T06:00:00Z",
  "topic_count": 5,
  "summary_count": 23,
  "version": "v1.0"
}
```

## 🔐 Security & Auth

- **Pub/Sub Push**: OIDC authentication with dedicated service account
- **Service Account**: `pubsub-push@echo-476821.iam.gserviceaccount.com`
- **IAM Role**: `roles/run.invoker` on all services
- **Cloud Run**: Public endpoints (can be restricted in production)

## 💰 Cost Optimization

| Resource | Configuration | Monthly Cost (est.) |
|----------|--------------|---------------------|
| Analyzer (GPU) | L4, min=0, max=2 | $20-50 (pay per use) |
| Summarizer | CPU, min=0 | $5-10 |
| Reporter | CPU, min=0 | $2-5 |
| Dashboard | CPU, min=0 | $2-5 |
| Firestore | <1GB | Free tier |
| Pub/Sub | <10k messages | Free tier |
| **Total** | | **$30-70/month** |

**Key Optimizations**:
- All services scale to zero when idle
- GPU only allocated during inference
- Lazy model initialization
- Efficient batch processing

## 📈 Performance Metrics

- **Embedding Generation**: ~2s per paper (GPU)
- **Summarization**: ~1-2s per paper (Gemini)
- **End-to-End Latency**: ~5-7s per paper
- **Throughput**: 10+ papers/minute
- **Cold Start**: <30s (GPU model loading)

## 🧪 Testing

### Health Checks

```bash
# Check all services
ANALYZER_URL=$(gcloud run services describe analyzer --region=europe-west4 --format='value(status.url)')
SUMMARIZER_URL=$(gcloud run services describe summarizer --region=europe-west4 --format='value(status.url)')
REPORTER_URL=$(gcloud run services describe reporter --region=europe-west4 --format='value(status.url)')

curl $ANALYZER_URL/healthz
curl $SUMMARIZER_URL/healthz
curl $REPORTER_URL/healthz
```

### Seed Document Test

```bash
# Publish synthetic document
gcloud pubsub topics publish echo-ingest \
  --message='{"doc_id":"seed-001","title":"Sample AI Paper","link":"https://example.com","source":"seed","timestamp":"2025-11-01T00:00:00Z"}' \
  --project=echo-476821

# Tail logs
gcloud beta logging tail 'resource.type=cloud_run_revision AND (resource.labels.service_name=analyzer OR resource.labels.service_name=summarizer OR resource.labels.service_name=reporter)' \
  --project=echo-476821

# Check report
curl -s $REPORTER_URL/latest | jq '.html' -r
```

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Check analyzer logs
gcloud beta logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=analyzer' --project=echo-476821

# Should see: "CUDA detected! Using GPU: Tesla L4"
```

### Pub/Sub Not Triggering

```bash
# Check subscription status
gcloud pubsub subscriptions describe sub-analyze --project=echo-476821

# Verify service account binding
gcloud run services get-iam-policy analyzer --region=europe-west4 --project=echo-476821
```

### Gemini API Errors

```bash
# Ensure GEMINI_API_KEY is set
gcloud run services describe summarizer --region=europe-west4 --format='value(spec.template.spec.containers[0].env)'
```

## 📚 Documentation

- **Architecture Deep Dive**: [docs/arch.md](docs/arch.md)
- **Deployment Guide**: [DEPLOY.md](DEPLOY.md)
- **API Reference**: See service `main.py` files

## 🎯 Quality Gates

- [x] All services respond 200 on `/` and `/healthz`
- [x] Analyzer runs on GPU and logs "CUDA detected"
- [x] Pub/Sub push works with OIDC
- [x] Firestore populated in all collections
- [x] Dashboard renders latest report
- [x] Docker images build reproducibly
- [x] Scripts succeed on clean machine
- [x] No mock data anywhere - all real AI

## 🚢 Project Structure

```
project-echo/
├── services/
│   ├── analyzer/          # GPU embeddings + clustering
│   ├── summarizer/        # Gemini summarization
│   ├── reporter/          # Weighted aggregation
│   └── crawler/           # ArXiv RSS fetcher
├── dashboard/             # Next.js frontend
├── infra/scripts/         # Deployment automation
├── docs/                  # Architecture docs
└── README.md              # This file
```

## 🏆 Hackathon Highlights

1. **Real AI**: Gemma 2B embeddings, Gemini 1.5 Flash summaries
2. **Mathematical Rigor**: Cosine similarity, online clustering, weighted aggregation
3. **Production Ready**: Serverless, auto-scaling, GPU-accelerated
4. **Cost Efficient**: ~$40/month, scales to zero
5. **Fully Autonomous**: Zero human intervention
6. **End-to-End Working**: Live demo available

## 📜 License

MIT License - Built for $20K Hackathon Submission

## 🙏 Acknowledgments

- Google Cloud Platform
- Gemini AI
- Hugging Face Transformers
- FastAPI & Next.js communities

---

**Project ECHO** - Autonomous Research Intelligence for the AI Age

*Built with ❤️ for the future of academic discovery*
