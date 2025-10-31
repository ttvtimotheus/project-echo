from fastapi import FastAPI, Request
from google.cloud import firestore, pubsub_v1
import os, json, base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Lazy initialization
_db = None
_publisher = None
_topic_path_out = None

def get_db():
    """Lazy initialize and return Firestore client."""
    global _db
    if _db is None:
        logger.info("Initializing Firestore client")
        _db = firestore.Client()
    return _db

def get_publisher():
    """Lazy initialize and return Pub/Sub publisher and topic path."""
    global _publisher, _topic_path_out
    if _publisher is None:
        logger.info("Initializing Pub/Sub publisher")
        _publisher = pubsub_v1.PublisherClient()
        project_id = os.environ.get("GCP_PROJECT", "echo-476821")
        topic_out = "echo-summarized"
        _topic_path_out = _publisher.topic_path(project_id, topic_out)
        logger.info(f"Publisher initialized for topic: {_topic_path_out}")
    return _publisher, _topic_path_out

@app.on_event("startup")
async def startup_event():
    """Log all registered routes on startup."""
    logger.info("Summarizer service starting up")
    logger.info(f"PORT environment variable: {os.getenv('PORT', '8080')}")
    logger.info(f"GCP_PROJECT environment variable: {os.getenv('GCP_PROJECT', 'echo-476821')}")
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"  {','.join(route.methods)} {route.path}")

@app.get("/")
def root():
    """Root endpoint to verify service is running."""
    return {"service": "summarizer", "ok": True}

@app.get("/healthz")
def health():
    """Health check endpoint."""
    return {"ok": True}

@app.post("/summarize")
async def summarize(request: Request):
    """Summarize a document. Accepts Pub/Sub push or direct JSON."""
    try:
        logger.info("Summarize endpoint called")
        data = await request.json()
        
        # Decode Pub/Sub push format if present
        if "message" in data and "data" in data["message"]:
            payload = json.loads(base64.b64decode(data["message"]["data"]).decode("utf-8"))
            logger.info(f"Decoded Pub/Sub payload: {payload}")
        else:
            payload = data
            logger.info(f"Direct JSON payload: {payload}")

        doc_id = payload.get("doc_id")
        if not doc_id:
            logger.warning("Missing doc_id in payload")
            return {"ok": False, "error": "missing doc_id"}

        db = get_db()
        
        # Retrieve document and analysis
        doc = db.collection("documents").document(doc_id).get()
        analysis = db.collection("analyses").document(doc_id).get()
        
        title = doc.to_dict().get("title", "Untitled") if doc.exists else "Untitled"
        topics = analysis.to_dict().get("topics", ["general"]) if analysis.exists else ["general"]

        # Generate summary
        summary_text = f"{title}. Topic: {topics[0]}."
        
        # Store summary
        db.collection("summaries").document(doc_id).set({
            "doc_id": doc_id,
            "summary": summary_text,
            "topics": topics,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Summary created for doc_id: {doc_id}")

        # Publish to next topic
        publisher, topic_path = get_publisher()
        message_data = json.dumps({"doc_id": doc_id}).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        future.result()  # Wait for publish to complete
        
        logger.info(f"Published to echo-summarized for doc_id: {doc_id}")
        
        return {"ok": True, "doc_id": doc_id, "summary": summary_text}
    
    except Exception as e:
        logger.error(f"Error summarizing document: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting summarizer on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
