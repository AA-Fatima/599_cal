import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from config import settings
from models.schemas import (
    ChatRequest, ChatResponse, DishCreate, MissingDishLog,
    GPTResponse, Modification
)
from services.openai_service import OpenAIService
from services.usda_lookup import UsdaLookupService
from services.dish_service import DishService
from services.fallback_service import FallbackService
from services.missing_logger import MissingLoggerService

# Initialize FastAPI app
app = FastAPI(
    title="Calorie Calculator Chatbot API",
    description="AI-powered calorie calculator using OpenAI GPT and USDA dataset",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
usda_lookup = UsdaLookupService(settings.USDA_FOUND_PATH)
dish_service = DishService(settings.DISHES_XLSX_PATH, usda_lookup)
openai_service = OpenAIService(settings.OPENAI_API_KEY)
fallback_service = FallbackService(dish_service)
missing_logger = MissingLoggerService()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Calorie Calculator Chatbot API",
        "version": "1.0.0",
        "endpoints": [
            "/api/chat",
            "/api/dishes",
            "/api/dishes/{name}",
            "/api/missing-dishes",
            "/api/usda/search"
        ]
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main endpoint: Receive user query and return calorie calculation
    
    This endpoint:
    1. Sends query to OpenAI GPT for parsing
    2. Looks up dish in local dataset or uses GPT suggestions
    3. Calculates nutritional values from USDA dataset
    4. Returns structured response with exact format
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Try OpenAI first
        gpt_response = openai_service.parse_query(request.query)
        
        if gpt_response:
            # Calculate calories from GPT response
            result = dish_service.calculate_from_gpt(gpt_response)
            
            # Check if dish was found in dataset
            dish_data = dish_service.find_dish_by_name(gpt_response.food_item)
            if not dish_data:
                # Log as missing dish
                missing_logger.log_missing_dish(
                    dish_name=gpt_response.food_item,
                    user_query=request.query,
                    gpt_ingredients=gpt_response.ingredients
                )
            
            return result
        
    except Exception as e:
        print(f"OpenAI API failed: {e}")
    
    # Fallback 1: Try fuzzy matching
    try:
        fuzzy_result = fallback_service.fuzzy_match_dish(request.query)
        if fuzzy_result:
            result = dish_service.calculate_from_gpt(fuzzy_result)
            result.notes.append("Using fuzzy match fallback")
            return result
    except Exception as e:
        print(f"Fuzzy match failed: {e}")
    
    # Fallback 2: Try simple food extraction
    try:
        simple_result = fallback_service.extract_simple_food(request.query)
        if simple_result:
            result = dish_service.calculate_from_gpt(simple_result)
            result.notes.append("Using simple food extraction fallback")
            return result
    except Exception as e:
        print(f"Simple extraction failed: {e}")
    
    # Fallback 3: Return helpful error
    raise HTTPException(
        status_code=400,
        detail={
            "error": "Could not understand your query",
            "message": "Please try rephrasing your question. For example: 'Calculate calories for chicken shawarma' or 'How many calories in rice with vegetables?'",
            "suggestions": [
                "Be specific about the dish name",
                "Mention quantities if known (e.g., '100g rice')",
                "Specify any modifications (e.g., 'without onions', 'extra tomato')"
            ]
        }
    )


@app.get("/api/dishes")
def list_dishes():
    """List all dishes in the dataset"""
    dishes = dish_service.get_all_dishes()
    return {
        "total": len(dishes),
        "dishes": dishes
    }


@app.get("/api/dishes/{name}")
def get_dish(name: str):
    """Get specific dish details by name"""
    dish = dish_service.find_dish_by_name(name)
    if not dish:
        raise HTTPException(status_code=404, detail=f"Dish '{name}' not found")
    return dish


@app.post("/api/dishes")
def create_dish(dish: DishCreate):
    """Add new dish to dataset (admin endpoint)"""
    try:
        new_dish = dish_service.add_dish(
            dish_name=dish.dish_name,
            country=dish.country,
            ingredients=dish.ingredients
        )
        return {
            "message": "Dish added successfully",
            "dish": new_dish
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/missing-dishes")
def get_missing_dishes():
    """Get list of logged missing dishes"""
    logs = missing_logger.get_all_logs()
    return {
        "total": len(logs),
        "missing_dishes": [log.dict() for log in logs]
    }


@app.get("/api/usda/search")
def search_usda(q: str = Query(..., min_length=2, description="Search query for ingredient")):
    """
    Search USDA ingredients by name (for autocomplete)
    
    Returns list of matching ingredients with fdc_id and name
    """
    results = usda_lookup.search_autocomplete(q, limit=20)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
