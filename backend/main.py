import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.pipeline import pipeline
from services.missing_log import missing_log

app = FastAPI(title="Calories Chatbot API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalculateRequest(BaseModel):
    query: str
    session_id: str | None = None

@app.post("/api/calculate")
def calculate(req: CalculateRequest):
    session_id = req.session_id or str(uuid.uuid4())
    result = pipeline.handle(req.query, session_id)
    if result.get("needs_clarification"):
        missing_log.log(req.query, result)
    return result | {"session_id": session_id}

@app.get("/api/missing")
def list_missing():
    return missing_log.items