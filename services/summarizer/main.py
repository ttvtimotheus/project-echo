from fastapi import FastAPI, Request
from google.cloud import firestore, pubsub_v1
import os, json, base64, time
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Lazy initialization
_db = None
_publisher = None
_topic_path_out = None
_gemini_model = None

# Gemini configuration
GEMINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_MAX_TOKENS = 500

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

def get_gemini_model():
    """Lazy initialize and return Gemini model."""
    global _gemini_model
    if _gemini_model is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set, summaries will be simple")
            return None
        
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        logger.info(f"Gemini model {GEMINI_MODEL_NAME} initialized")
    
    return _gemini_model

def generate_summary_with_gemini(title: str, abstract: str, topics: list) -> str:
    """
    Generate abstractive summary using Gemini 1.5 Flash.
    Conditioned on topic labels with strict style prompt.
    """
    model = get_gemini_model()
    
    if model is None:
        # Fallback to simple summary
        return f"{title}. Topics: {', '.join(topics)}."
    
    # Construct prompt
    topics_str = ', '.join(topics)
    prompt = f"""You are a research summarizer. Given the following research paper details, create a concise, professional summary in ONE sentence.

Title: {title}
Abstract: {abstract}
Assigned Topics: {topics_str}

Provide a single-sentence summary that captures the key contribution and relates to the assigned topics. Be precise and academic.

Summary:"""
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=GEMINI_MAX_TOKENS,
                temperature=0.3,
            )
        )
        
        summary = response.text.strip()
        logger.info(f"Gemini generated summary: {summary[:100]}...")
        return summary
    
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        # Fallback
        return f"{title}. Topics: {topics_str}."

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
        
        if not doc.exists:
            logger.warning(f"Document not found: {doc_id}")
            return {"ok": False, "error": "document not found"}
        
        doc_data = doc.to_dict()
        title = doc_data.get("title", "Untitled")
        abstract = doc_data.get("summary", "")
        topics = analysis.to_dict().get("topics", ["general"]) if analysis.exists else ["general"]

        # Generate summary with Gemini 1.5 Flash
        start_time = time.time()
        summary_text = generate_summary_with_gemini(title, abstract, topics)
        summary_time = time.time() - start_time
        logger.info(f"Summary generation took {summary_time:.2f}s")
        
        # Store summary
        db.collection("summaries").document(doc_id).set({
            "doc_id": doc_id,
            "summary": summary_text,
            "topics": topics,
            "model_used": GEMINI_MODEL_NAME,
            "summary_time": summary_time,
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
