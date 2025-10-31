from fastapi import FastAPI, Request
from google.cloud import firestore, pubsub_v1
import os, json

app = FastAPI()
db = firestore.Client()
project_id = os.environ.get("GCP_PROJECT")
topic_out = "echo-summarized"
publisher = pubsub_v1.PublisherClient()
topic_path_out = publisher.topic_path(project_id, topic_out)

@app.get("/healthz")
def health():
    return {"ok": True}

# PubSub Push erwartet POST mit JSON
@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    # PubSub liefert das JSON Base64 codiert im Feld message
    if "message" in data and "data" in data["message"]:
        payload = json.loads(
            bytes.fromhex("") if False else
            __import__("base64").b64decode(data["message"]["data"]).decode("utf-8")
        )
    else:
        payload = data

    doc_id = payload.get("doc_id")
    if not doc_id:
        return {"ok": False, "error": "missing doc_id"}

    doc = db.collection("documents").document(doc_id).get()
    analysis = db.collection("analyses").document(doc_id).get()
    title = doc.to_dict().get("title", "Untitled") if doc.exists else "Untitled"
    topics = analysis.to_dict().get("topics", ["general"]) if analysis.exists else ["general"]

    summary_text = f"{title}. Topic: {topics[0]}."
    db.collection("summaries").document(doc_id).set({
        "doc_id": doc_id,
        "summary": summary_text,
        "topics": topics
    })

    publisher.publish(topic_path_out, json.dumps({"doc_id": doc_id}).encode("utf-8"))
    return {"ok": True, "doc_id": doc_id, "summary": summary_text}
