from fastapi import FastAPI, Request
from google.cloud import firestore, pubsub_v1
import os, json, base64, time
import logging
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Lazy initialization
_db = None
_publisher = None
_topic_path_out = None
_model = None
_tokenizer = None
_device = None

# Clustering parameters
SIMILARITY_THRESHOLD = 0.8  # tau from spec
MAX_TOPICS = 20

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

def get_model():
    """Lazy initialize and return Gemma 2B model for embeddings."""
    global _model, _tokenizer, _device
    if _model is None:
        logger.info("Initializing Gemma 2B model for embeddings")
        
        # Check for GPU
        if torch.cuda.is_available():
            _device = torch.device("cuda")
            logger.info(f"CUDA detected! Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            _device = torch.device("cpu")
            logger.warning("CUDA not available, using CPU")
        
        # Use a smaller model for embeddings (sentence-transformers style)
        model_name = "google/gemma-2b"  # Will use this for embedding generation
        
        try:
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float16)
            _model.to(_device)
            _model.eval()
            logger.info(f"Model loaded on {_device}")
        except Exception as e:
            logger.error(f"Failed to load Gemma model: {e}")
            # Fallback to a smaller model
            logger.info("Falling back to sentence-transformers model")
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModel.from_pretrained(model_name)
            _model.to(_device)
            _model.eval()
        
    return _model, _tokenizer, _device

def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding vector for text using Gemma 2B.
    Returns: numpy array of shape (embedding_dim,)
    """
    model, tokenizer, device = get_model()
    
    # Tokenize and encode
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate embeddings (mean pooling of last hidden state)
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        embedding_vector = embeddings.cpu().numpy().flatten()
    
    return embedding_vector

def load_centroids(db):
    """
    Load existing topic centroids from Firestore.
    Returns: dict {topic_name: centroid_vector}
    """
    centroids = {}
    docs = db.collection("centroids").stream()
    for doc in docs:
        data = doc.to_dict()
        topic_name = doc.id
        centroid_vector = np.array(data.get("vector", []))
        if len(centroid_vector) > 0:
            centroids[topic_name] = centroid_vector
    return centroids

def save_centroid(db, topic_name: str, centroid_vector: np.ndarray):
    """
    Save or update a centroid in Firestore.
    """
    db.collection("centroids").document(topic_name).set({
        "vector": centroid_vector.tolist(),
        "updated_at": firestore.SERVER_TIMESTAMP,
        "dimension": len(centroid_vector)
    })

def compute_cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute cosine similarity: S(i,j) = (v_i · v_j) / (||v_i|| * ||v_j||)
    """
    return cosine_similarity(v1.reshape(1, -1), v2.reshape(1, -1))[0, 0]

def assign_topic(embedding: np.ndarray, centroids: dict) -> tuple:
    """
    Assign document to topic based on centroid matching.
    Returns: (topic_name, similarity_score)
    If all similarities < SIMILARITY_THRESHOLD, returns (None, max_score)
    """
    if not centroids:
        return None, 0.0
    
    best_topic = None
    best_score = -1.0
    
    for topic_name, centroid in centroids.items():
        score = compute_cosine_similarity(embedding, centroid)
        if score > best_score:
            best_score = score
            best_topic = topic_name
    
    # Check threshold
    if best_score < SIMILARITY_THRESHOLD:
        return None, best_score
    
    return best_topic, best_score

def create_new_topic(db, embedding: np.ndarray) -> str:
    """
    Create a new topic with this embedding as centroid.
    Generate a simple topic name based on count.
    """
    # Count existing topics
    centroids = load_centroids(db)
    topic_id = len(centroids) + 1
    
    if topic_id > MAX_TOPICS:
        # If we hit max topics, assign to most similar existing one
        logger.warning(f"Max topics ({MAX_TOPICS}) reached, forcing assignment")
        return None
    
    topic_name = f"topic_{topic_id:02d}"
    save_centroid(db, topic_name, embedding)
    logger.info(f"Created new topic: {topic_name}")
    
    return topic_name

def update_centroid(db, topic_name: str, new_embedding: np.ndarray, alpha=0.1):
    """
    Update centroid using exponential moving average.
    c_k_new = (1 - alpha) * c_k_old + alpha * v_new
    """
    centroids = load_centroids(db)
    if topic_name in centroids:
        old_centroid = centroids[topic_name]
        new_centroid = (1 - alpha) * old_centroid + alpha * new_embedding
        save_centroid(db, topic_name, new_centroid)
        logger.info(f"Updated centroid for {topic_name}")

def analyze_document(doc_data, db):
    """
    Analyze document using Gemma 2B embeddings and clustering.
    Returns: (topics_list, score, embedding_ref)
    """
    # Generate text from document
    text = f"{doc_data.get('title', '')} {doc_data.get('summary', '')}"
    
    # Generate embedding
    embedding = generate_embedding(text)
    
    # Load existing centroids
    centroids = load_centroids(db)
    
    # Assign to topic
    topic_name, score = assign_topic(embedding, centroids)
    
    if topic_name is None:
        # Create new topic
        topic_name = create_new_topic(db, embedding)
        if topic_name is None:
            # Max topics reached, force assign
            topic_name, score = assign_topic(embedding, centroids)
        else:
            score = 1.0  # New topic, perfect match
    else:
        # Update centroid
        update_centroid(db, topic_name, embedding)
    
    # Store embedding reference (we don't store full embedding to save space)
    embedding_ref = f"embeddings/{doc_data.get('doc_id', 'unknown')}"
    
    return [topic_name], float(score * 100), embedding_ref

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
        
        # Analyze document with AI
        start_time = time.time()
        topics, score, embedding_ref = analyze_document(doc_data, db)
        analysis_time = time.time() - start_time
        logger.info(f"Analysis took {analysis_time:.2f}s")
        
        # Store analysis
        analysis_data = {
            "doc_id": doc_id,
            "topics": topics,
            "score": score,
            "embedding_ref": embedding_ref,
            "analysis_time": analysis_time,
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
