from fastapi import FastAPI, Request
from google.cloud import firestore
from datetime import datetime, timedelta
import json, base64, os

app = FastAPI()
db = firestore.Client()

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/report")
async def report(request: Request):
    body = await request.json()
    if "message" in body and "data" in body["message"]:
        _ = json.loads(base64.b64decode(body["message"]["data"]).decode("utf-8"))

    items = []
    for s in db.collection("summaries").stream():
        d = s.to_dict()
        items.append(f"<li>{d.get('summary','')}</li>")

    html = "<h1>Daily ECHO</h1><ul>" + "".join(items) + "</ul>"
    db.collection("reports").add({"html": html, "created_at": firestore.SERVER_TIMESTAMP})
    return {"ok": True, "count": len(items)}

@app.get("/latest")
def latest():
    qs = db.collection("reports").order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
    for doc in qs:
        return {"html": doc.to_dict().get("html", "")}
    return {"html": ""}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
