from rapidfuzz import process, fuzz
from sqlalchemy import func, text
from db import SessionLocal
from models import Dish

class MatchResult:
    def __init__(self):
        self.found_dish = None
        self.single_ingredient = None
        self.entities = None
        self.quantities = None
        self.text = None

class CandidateResolver:
    def __init__(self, dish_service):
        self.ds = dish_service
        self.db = None
    
    def get_db(self):
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def resolve(self, entities, quantities, text):
        """Resolve entities to dish or ingredient."""
        mr = MatchResult()
        mr.entities = entities
        mr.quantities = quantities
        mr.text = text

        # Try to find dish if dish entities exist
        if entities.get("dishes"):
            dish_query = " ".join(entities["dishes"]).lower().strip()
            
            # Use dish service to find dish with pg_trgm
            dish = self.ds.find_dish_by_name(dish_query)
            if dish:
                mr.found_dish = dish
                return mr
            
            # Fallback to rapidfuzz search
            db = self.get_db()
            all_dishes = db.query(Dish).limit(1000).all()
            dish_names = [d.dish_name for d in all_dishes]
            
            if dish_names:
                match = process.extractOne(dish_query, dish_names, scorer=fuzz.WRatio, score_cutoff=70)
                if match:
                    dish = db.query(Dish).filter(Dish.dish_name == match[0]).first()
                    if dish:
                        mr.found_dish = dish
                        return mr

        # If no dish found, treat as single ingredient
        if entities.get("ingredients"):
            ing_query = " ".join(entities["ingredients"])
            mr.single_ingredient = ing_query
            return mr

        return mr