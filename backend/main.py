import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.pipeline import pipeline
from services.missing_log import missing_log

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Calories Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000", "*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalculateRequest(BaseModel):
    query: str
    session_id: str | None = None

@app.post("/api/calculate")
def calculate(req: CalculateRequest):
    """Calculate calories for a dish or ingredient query."""
    try:
        session_id = req.session_id or str(uuid.uuid4())
        logger.info(f"Processing query: {req.query[:50]}... (session: {session_id})")
        
        result = pipeline.handle(req.query, session_id)
        
        if result.get("needs_clarification"):
            missing_log.log(req.query, result)
            logger.info(f"Clarification needed for query: {req.query[:50]}...")
        else:
            logger.info(f"Successfully computed calories: {result.get('total_calories', 0)} kcal")
        
        # Placeholder for metrics hooks
        # TODO: Add metrics collection here (e.g., prometheus, statsd)
        # metrics.increment("queries.total")
        # metrics.histogram("queries.calories", result.get("total_calories", 0))
        
        return result | {"session_id": session_id}
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return {
            "needs_clarification": True,
            "message": "An error occurred processing your request.",
            "session_id": req.session_id or str(uuid.uuid4())
        }

@app.get("/api/missing")
def list_missing():
    """Get list of queries for missing dishes."""
    try:
        logger.info("Fetching missing dishes log")
        return missing_log.items
    except Exception as e:
        logger.error(f"Error fetching missing dishes: {str(e)}", exc_info=True)
        return []

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}