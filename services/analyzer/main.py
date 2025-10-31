# services/analyzer/main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/healthz")
def h():
    return {"ok": True}
