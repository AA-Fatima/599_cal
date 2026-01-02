import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from config import settings
from models.schemas import (
    ChatRequest, ChatResponse, DishResponse, AddDishRequest,
    MissingDishLog, GPTResponse, Modifications
)
from services.openai_service import openai_service
from services.usda_lookup import UsdaLookup
from services.dish_service import DishService
from services.fallback_service import FallbackService
from services.missing_logger import missing_logger

# Initialize services
usda_lookup = UsdaLookup(settings.USDA_FOUND_PATH)
dish_service = DishService(usda_lookup, settings.DISHES_XLSX_PATH)
fallback_service = FallbackService([d["dish_name"] for d in dish_service.get_all_dishes()])

app = FastAPI(title="Calorie Chatbot API with OpenAI GPT")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Calorie Chatbot API with OpenAI GPT is running"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint - receive user query and return calorie calculation
    
    Flow:
    1. Try OpenAI GPT to parse query
    2. If GPT fails, use fuzzy matching fallback
    3. If that fails, use simple entity extraction
    4. If all fail, return error message
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    gpt_response: GPTResponse = None
    
    # Try OpenAI GPT first
    try:
        gpt_response = openai_service.parse_food_query(request.query)
    except Exception as e:
        print(f"OpenAI service error: {e}")
    
    # Fallback 1: Fuzzy matching
    if not gpt_response:
        gpt_response = fallback_service.fuzzy_match_dish(request.query)
    
    # Fallback 2: Simple entity extraction
    if not gpt_response:
        gpt_response = fallback_service.simple_entity_extraction(request.query)
    
    # If all fallbacks failed
    if not gpt_response:
        raise HTTPException(
            status_code=400,
            detail="Could not understand your query. Please try rephrasing with a specific food or dish name."
        )
    
    # Check if dish exists in database
    dish = dish_service.find_dish_by_name(gpt_response.food_item)
    
    # Log missing dish
    if not dish:
        missing_logger.log_missing_dish(
            gpt_response.food_item,
            request.query,
            gpt_response.ingredients
        )
    
    # Calculate nutrition
    try:
        response = dish_service.calculate_nutrition(gpt_response)
        return response
    except Exception as e:
        print(f"Calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating nutrition: {str(e)}"
        )

@app.get("/api/dishes", response_model=List[DishResponse])
def list_dishes():
    """List all dishes in the dataset"""
    return dish_service.get_all_dishes()

@app.get("/api/dishes/{name}", response_model=DishResponse)
def get_dish(name: str):
    """Get specific dish details by name"""
    dish = dish_service.find_dish_by_name(name)
    if not dish:
        raise HTTPException(status_code=404, detail=f"Dish '{name}' not found")
    return dish

@app.post("/api/dishes", response_model=DishResponse)
def add_dish(request: AddDishRequest):
    """Add new dish (admin endpoint)"""
    try:
        # Check if dish already exists
        existing = dish_service.find_dish_by_name(request.dish_name)
        if existing:
            raise HTTPException(status_code=400, detail=f"Dish '{request.dish_name}' already exists")
        
        # Prepare ingredients
        ingredients = [
            {"usda_name": ing.usda_name, "weight_g": ing.weight_g}
            for ing in request.ingredients
        ]
        
        new_dish = dish_service.add_dish(request.dish_name, request.country, ingredients)
        return new_dish
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding dish: {str(e)}")

@app.get("/api/missing-dishes", response_model=List[MissingDishLog])
def get_missing_dishes():
    """Get logged missing dishes"""
    return missing_logger.get_logs()

@app.get("/api/usda/search")
def search_usda(q: str, limit: int = 10):
    """Search USDA ingredients by name (for autocomplete)"""
    if not q or len(q) < 2:
        return []
    
    results = usda_lookup.search(q, limit=limit)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
