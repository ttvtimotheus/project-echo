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
        topic_out = "echo-analyzed"
        _topic_path_out = _publisher.topic_path(project_id, topic_out)
        logger.info(f"Publisher initialized for topic: {_topic_path_out}")
    return _publisher, _topic_path_out

def analyze_document(doc_data):
    """
    Analyze document and extract topics.
    Simple keyword-based topic extraction for now.
    """
    text = f"{doc_data.get('title', '')} {doc_data.get('summary', '')}".lower()
    
    # Simple keyword-based topic detection
    topics = []
    keywords = {
        "machine learning": ["machine learning", "neural network", "deep learning", "ml"],
        "computer vision": ["computer vision", "image", "video", "visual"],
        "nlp": ["natural language", "nlp", "text", "language model"],
        "robotics": ["robot", "robotics", "autonomous"],
        "systems": ["system", "distributed", "architecture"],
        "security": ["security", "privacy", "cryptography"],
        "theory": ["theorem", "proof", "algorithm"]
    }
    
    for topic, words in keywords.items():
        if any(word in text for word in words):
            topics.append(topic)
    
    if not topics:
        topics = ["general"]
    
    # Calculate simple score based on text length
    score = min(100, len(text) / 10)
    
    return topics, score

@app.on_event("startup")
async def startup_event():
    """Log all registered routes on startup."""
    logger.info("Analyzer service starting up")
    logger.info(f"PORT environment variable: {os.getenv('PORT', '8080')}")
    logger.info(f"GCP_PROJECT environment variable: {os.getenv('GCP_PROJECT', 'echo-476821')}")
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"  {','.join(route.methods)} {route.path}")

@app.get("/")
def root():
    """Root endpoint to verify service is running."""
    return {"service": "analyzer", "ok": True}

@app.get("/healthz")
def health():
    """Health check endpoint."""
    return {"ok": True}

@app.post("/analyze")
async def analyze(request: Request):
    """Analyze a document. Accepts Pub/Sub push or direct JSON."""
    try:
        logger.info("Analyze endpoint called")
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
        
        # Retrieve document
        doc = db.collection("documents").document(doc_id).get()
        
        if not doc.exists:
            logger.warning(f"Document not found: {doc_id}")
            return {"ok": False, "error": f"document not found: {doc_id}"}
        
        doc_data = doc.to_dict()
        logger.info(f"Analyzing document: {doc_data.get('title', 'Untitled')}")
        
        # Analyze document
        topics, score = analyze_document(doc_data)
        
        # Store analysis
        analysis_data = {
            "doc_id": doc_id,
            "topics": topics,
            "score": score,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        db.collection("analyses").document(doc_id).set(analysis_data)
        
        logger.info(f"Analysis created for doc_id: {doc_id}, topics: {topics}, score: {score}")

        # Publish to next topic
        publisher, topic_path = get_publisher()
        message_data = json.dumps({"doc_id": doc_id}).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        future.result()  # Wait for publish to complete
        
        logger.info(f"Published to echo-analyzed for doc_id: {doc_id}")
        
        return {"ok": True, "doc_id": doc_id, "topics": topics, "score": score}
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting analyzer on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
