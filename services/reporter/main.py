from fastapi import FastAPI, Request
from google.cloud import firestore
import json, base64, os
import logging

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

@app.post("/report")
async def report(request: Request):
    """Generate report from all summaries. Accepts Pub/Sub push or direct JSON."""
    try:
        logger.info("Report endpoint called")
        body = await request.json()
        
        # Decode Pub/Sub push format if present
        if "message" in body and "data" in body["message"]:
            payload = json.loads(base64.b64decode(body["message"]["data"]).decode("utf-8"))
            logger.info(f"Decoded Pub/Sub payload: {payload}")
        else:
            payload = body
            logger.info(f"Direct JSON payload: {payload}")

        db = get_db()
        items = []
        
        # Collect all summaries
        for s in db.collection("summaries").stream():
            d = s.to_dict()
            summary_text = d.get('summary', '')
            if summary_text:
                items.append(f"<li>{summary_text}</li>")
        
        # Build HTML report
        html = "<h1>Daily ECHO</h1><ul>" + "".join(items) + "</ul>"
        
        # Store report
        db.collection("reports").add({
            "html": html,
            "created_at": firestore.SERVER_TIMESTAMP,
            "summary_count": len(items)
        })
        
        logger.info(f"Report generated with {len(items)} summaries")
        return {"ok": True, "count": len(items)}
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

@app.get("/latest")
def latest():
    """Get the most recent report."""
    try:
        logger.info("Latest endpoint called")
        db = get_db()
        
        qs = db.collection("reports").order_by(
            "created_at", 
            direction=firestore.Query.DESCENDING
        ).limit(1).stream()
        
        for doc in qs:
            data = doc.to_dict()
            logger.info(f"Retrieved report with {data.get('summary_count', 0)} summaries")
            return {"html": data.get("html", "")}
        
        logger.info("No reports found")
        return {"html": ""}
    
    except Exception as e:
        logger.error(f"Error retrieving latest report: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting reporter on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
