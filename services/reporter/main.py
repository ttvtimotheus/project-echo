from fastapi import FastAPI, Request
from google.cloud import firestore
import json, base64, os, time
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Lazy Firestore client initialization
_db = None

def get_db():
    """Lazy initialize and return Firestore client."""
    global _db
    if _db is None:
        logger.info("Initializing Firestore client")
        _db = firestore.Client()
    return _db

@app.on_event("startup")
async def startup_event():
    """Log all registered routes on startup."""
    logger.info("Reporter service starting up")
    logger.info(f"PORT environment variable: {os.getenv('PORT', '8080')}")
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"  {','.join(route.methods)} {route.path}")

@app.get("/")
def root():
    """Root endpoint to verify service is running."""
    return {"service": "reporter", "ok": True}

@app.get("/healthz")
def health():
    """Health check endpoint."""
    return {"ok": True}

def compute_topic_weights(summaries: list) -> dict:
    """
    Compute weighted topic distribution.
    alpha_k = |C_k| / sum_j |C_j|
    """
    topic_counts = defaultdict(int)
    
    for summary in summaries:
        topics = summary.get('topics', [])
        for topic in topics:
            topic_counts[topic] += 1
    
    total = sum(topic_counts.values())
    if total == 0:
        return {}
    
    weights = {topic: count / total for topic, count in topic_counts.items()}
    return weights

def generate_html_report(summaries: list, weights: dict) -> str:
    """
    Generate weighted HTML report grouped by topics.
    """
    # Group summaries by primary topic
    topic_groups = defaultdict(list)
    
    for summary in summaries:
        topics = summary.get('topics', ['general'])
        primary_topic = topics[0] if topics else 'general'
        topic_groups[primary_topic].append(summary)
    
    # Sort topics by weight (descending)
    sorted_topics = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    # Build HTML
    html_parts = ["<h1>ECHO Research Intelligence Report</h1>"]
    html_parts.append(f"<p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</em></p>")
    html_parts.append(f"<p><strong>Total Papers:</strong> {len(summaries)} | <strong>Topics:</strong> {len(weights)}</p>")
    html_parts.append("<hr>")
    
    for topic, weight in sorted_topics:
        if topic in topic_groups:
            papers = topic_groups[topic]
            html_parts.append(f"<h2>{topic.replace('_', ' ').title()} ({len(papers)} papers, {weight*100:.1f}%)</h2>")
            html_parts.append("<ul>")
            
            for paper in papers:
                summary_text = paper.get('summary', 'No summary available')
                html_parts.append(f"<li>{summary_text}</li>")
            
            html_parts.append("</ul>")
    
    return "".join(html_parts)

@app.post("/report")
async def report(request: Request):
    """Generate weighted report from recent summaries. Accepts Pub/Sub push or direct JSON."""
    try:
        logger.info("Report endpoint called")
        start_time = time.time()
        body = await request.json()
        
        # Decode Pub/Sub push format if present
        if "message" in body and "data" in body["message"]:
            payload = json.loads(base64.b64decode(body["message"]["data"]).decode("utf-8"))
            logger.info(f"Decoded Pub/Sub payload: {payload}")
        else:
            payload = body
            logger.info(f"Direct JSON payload: {payload}")

        db = get_db()
        summaries = []
        
        # Time window: last 24 hours (or all if not enough)
        time_threshold = datetime.now() - timedelta(hours=24)
        
        # Collect summaries
        for doc in db.collection("summaries").stream():
            data = doc.to_dict()
            # Check timestamp
            created_at = data.get('created_at')
            if created_at and hasattr(created_at, 'timestamp'):
                if datetime.fromtimestamp(created_at.timestamp()) < time_threshold:
                    continue  # Skip old summaries
            
            summaries.append(data)
        
        if not summaries:
            logger.warning("No recent summaries found, fetching all")
            summaries = [doc.to_dict() for doc in db.collection("summaries").stream()]
        
        # Compute topic weights
        weights = compute_topic_weights(summaries)
        
        # Generate HTML report
        html = generate_html_report(summaries, weights)
        
        # Store report
        report_data = {
            "html": html,
            "created_at": firestore.SERVER_TIMESTAMP,
            "topic_count": len(weights),
            "summary_count": len(summaries),
            "version": "v1.0"
        }
        db.collection("reports").add(report_data)
        
        generation_time = time.time() - start_time
        logger.info(f"Report generated: {len(summaries)} summaries, {len(weights)} topics in {generation_time:.2f}s")
        
        return {
            "ok": True,
            "count": len(summaries),
            "topics": len(weights),
            "generation_time": generation_time
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

@app.get("/latest")
def latest():
    """Return the latest report with metadata."""
    try:
        db = get_db()
        # Get most recent report (ordered by created_at desc, limit 1)
        reports = db.collection("reports").order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for report in reports:
            data = report.to_dict()
            return {
                "html": data.get("html", "No report available"),
                "topic_count": data.get("topic_count", 0),
                "summary_count": data.get("summary_count", 0),
                "created_at": data.get("created_at").isoformat() if data.get("created_at") else None,
                "version": data.get("version", "unknown")
            }
        
        return {
            "html": "<h1>No reports available yet</h1><p>Run the crawler to generate papers.</p>",
            "topic_count": 0,
            "summary_count": 0,
            "created_at": None,
            "version": "v1.0"
        }
    
    except Exception as e:
        logger.error(f"Error retrieving latest report: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting reporter on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
