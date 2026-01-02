from pydantic import BaseModel
from typing import List, Optional, Dict

class Modification(BaseModel):
    remove: List[str] = []
    add: List[str] = []

class GPTResponse(BaseModel):
    food_item: str
    modifications: Modification = Modification()
    ingredients: List[str] = []

class IngredientDetail(BaseModel):
    usda_fdc_id: int
    name: str
    weight_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float

class NutritionTotals(BaseModel):
    weight_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float

class ChatResponse(BaseModel):
    food_item: str
    ingredients: List[IngredientDetail]
    totals: NutritionTotals
    notes: List[str] = []

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class DishCreate(BaseModel):
    dish_name: str
    country: str
    ingredients: List[Dict]

class MissingDishLog(BaseModel):
    dish_name: str
    timestamp: str
    user_query: str
    gpt_suggested_ingredients: List[str]
