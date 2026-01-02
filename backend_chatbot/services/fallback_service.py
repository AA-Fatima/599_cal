from typing import Optional
from rapidfuzz import process, fuzz
from models.schemas import GPTResponse, Modifications

class FallbackService:
    def __init__(self, dish_names: list):
        """Initialize with list of known dish names for fuzzy matching"""
        self.dish_names = dish_names
    
    def fuzzy_match_dish(self, query: str) -> Optional[GPTResponse]:
        """
        Fallback 1: Use fuzzy matching to find dish in local dataset
        """
        query = query.lower().strip()
        
        # Try to find the dish name in the query
        match = process.extractOne(query, self.dish_names, scorer=fuzz.partial_ratio, score_cutoff=70)
        
        if match:
            dish_name = match[0]
            return GPTResponse(
                food_item=dish_name,
                modifications=Modifications(),
                ingredients=[]  # Will be filled from database
            )
        
        return None
    
    def simple_entity_extraction(self, query: str) -> Optional[GPTResponse]:
        """
        Fallback 2: Simple keyword-based entity extraction
        This is a very basic NER-like approach
        """
        query = query.lower()
        
        # Common food keywords
        food_keywords = [
            "chicken", "beef", "fish", "rice", "bread", "pasta", "pizza",
            "salad", "soup", "sandwich", "burger", "fries", "shawarma",
            "hummus", "falafel", "kebab", "tacos", "wrap"
        ]
        
        found_foods = [kw for kw in food_keywords if kw in query]
        
        if found_foods:
            # Use the first found food as the main item
            return GPTResponse(
                food_item=found_foods[0],
                modifications=Modifications(),
                ingredients=[found_foods[0]]
            )
        
        return None

fallback_service = None  # Will be initialized in main.py
