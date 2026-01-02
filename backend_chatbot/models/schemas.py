from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Modifications(BaseModel):
    remove: List[str] = []
    add: List[str] = []

class GPTResponse(BaseModel):
    food_item: str
    modifications: Modifications = Modifications()
    ingredients: List[str]

class IngredientDetail(BaseModel):
    name: str
    weight_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float

class Totals(BaseModel):
    weight_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    food_item: str
    ingredients: List[IngredientDetail]
    totals: Totals
    notes: List[str] = []

class DishIngredient(BaseModel):
    usda_name: str
    weight_g: float

class AddDishRequest(BaseModel):
    dish_name: str
    country: str
    ingredients: List[DishIngredient]

class DishResponse(BaseModel):
    dish_id: int
    dish_name: str
    country: str
    weight_g: float
    calories: float
    ingredients: List[Dict[str, Any]]

class MissingDishLog(BaseModel):
    dish_name: str
    user_query: str
    gpt_suggested_ingredients: List[str]
    timestamp: str
