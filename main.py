from fastapi import FastAPI
from pydantic import BaseModel
from pipeline import handle

app = FastAPI(title="TOLLGATE")

class Ask(BaseModel):
    query: str
    tenant: str = "public"

@app.post("/ask")
def ask(body: Ask):
    return handle(body.query, body.tenant)

@app.get("/health")
def health():
    return {"status": "ok"}