from typing import Optional
from rapidfuzz import process, fuzz
from models.schemas import GPTResponse, Modification
from services.dish_service import DishService

class FallbackService:
    def __init__(self, dish_service: DishService):
        self.dish_service = dish_service
    
    def fuzzy_match_dish(self, query: str) -> Optional[GPTResponse]:
        """Try to find dish using fuzzy string matching"""
        query_lower = query.lower().strip()
        
        # Get all dish names
        dish_names = [d["dish_name"] for d in self.dish_service.dishes]
        
        # Try fuzzy matching
        match = process.extractOne(query_lower, dish_names, scorer=fuzz.WRatio, score_cutoff=70)
        
        if match:
            matched_dish_name = match[0]
            dish = self.dish_service.find_dish_by_name(matched_dish_name)
            
            if dish:
                # Extract ingredient names from dish
                ingredient_names = [ing.get("name", "") for ing in dish.get("ingredients", [])]
                
                return GPTResponse(
                    food_item=dish["dish_name"],
                    modifications=Modification(),
                    ingredients=ingredient_names
                )
        
        return None
    
    def extract_simple_food(self, query: str) -> Optional[GPTResponse]:
        """Try to extract a simple food item from the query"""
        # Simple keyword extraction (basic fallback)
        query_lower = query.lower().strip()
        
        # Common food keywords that might be in the query
        common_foods = [
            "chicken", "beef", "rice", "bread", "tomato", "onion",
            "olive oil", "cheese", "fish", "egg", "potato", "pasta"
        ]
        
        for food in common_foods:
            if food in query_lower:
                return GPTResponse(
                    food_item=food,
                    modifications=Modification(),
                    ingredients=[food]
                )
        
        return None
