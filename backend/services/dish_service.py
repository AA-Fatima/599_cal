from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from models import UsdaItem, Dish, DishIngredient
from db import SessionLocal
from services.unit_map import to_grams
from services.cache import cached


class DishService:
    def __init__(self):
        self.session: Session = None
    
    def _get_session(self) -> Session:
        """Get or create database session."""
        if not self.session:
            self.session = SessionLocal()
        return self.session
    
    @cached(ttl=3600, key_prefix="usda_cal_name")
    def get_calories_by_name(self, name: str):
        """Get calories for ingredient by name using fuzzy match."""
        session = self._get_session()
        name_lower = name.lower().strip()
        
        # Try exact match first
        item = session.query(UsdaItem).filter(UsdaItem.name == name_lower).first()
        if item:
            return item.per_100g_calories
        
        # Try pg_trgm similarity search
        try:
            results = session.query(
                UsdaItem,
                func.similarity(UsdaItem.name, name_lower).label('sim')
            ).filter(
                func.similarity(UsdaItem.name, name_lower) > 0.3
            ).order_by(
                func.similarity(UsdaItem.name, name_lower).desc()
            ).limit(1).all()
            
            if results:
                return results[0][0].per_100g_calories
        except Exception:
            # pg_trgm not available, fallback to LIKE
            item = session.query(UsdaItem).filter(
                UsdaItem.name.ilike(f"%{name_lower}%")
            ).first()
            if item:
                return item.per_100g_calories
        
        return None
    
    @cached(ttl=3600, key_prefix="usda_cal_id")
    def get_calories_by_id(self, fdc_id: int):
        """Get calories for ingredient by USDA FDC ID."""
        session = self._get_session()
        item = session.query(UsdaItem).filter(UsdaItem.fdc_id == fdc_id).first()
        return item.per_100g_calories if item else None
    
    @cached(ttl=3600, key_prefix="dish")
    def get_dish_by_name(self, name: str):
        """Get dish by name using fuzzy match."""
        session = self._get_session()
        name_lower = name.lower().strip()
        
        # Try exact match first
        dish = session.query(Dish).filter(Dish.dish_name == name_lower).first()
        if dish:
            return self._dish_to_dict(dish)
        
        # Try pg_trgm similarity search
        try:
            results = session.query(
                Dish,
                func.similarity(Dish.dish_name, name_lower).label('sim')
            ).filter(
                func.similarity(Dish.dish_name, name_lower) > 0.3
            ).order_by(
                func.similarity(Dish.dish_name, name_lower).desc()
            ).limit(1).all()
            
            if results:
                return self._dish_to_dict(results[0][0])
        except Exception:
            # pg_trgm not available, fallback to LIKE
            dish = session.query(Dish).filter(
                Dish.dish_name.ilike(f"%{name_lower}%")
            ).first()
            if dish:
                return self._dish_to_dict(dish)
        
        return None
    
    def _dish_to_dict(self, dish: Dish):
        """Convert dish to dictionary with ingredients."""
        session = self._get_session()
        ingredients = session.query(DishIngredient).filter(
            DishIngredient.dish_id == dish.dish_id
        ).all()
        
        return {
            "dish_id": dish.dish_id,
            "dish_name": dish.dish_name,
            "country": dish.country,
            "ingredients": [
                {
                    "name": ing.ingredient_name,
                    "weight_g": ing.default_weight_g,
                    "usda_fdc_id": ing.usda_fdc_id
                }
                for ing in ingredients
            ]
        }

    def compute(self, match):
        """Compute calories for a dish or single ingredient."""
        if match.single_ingredient and not match.found_dish:
            ing = match.single_ingredient.lower()
            qty_grams = 100.0
            if match.quantities:
                q = match.quantities[0]
                qty_grams = to_grams(ing, q["qty"], q["unit"])
            per100 = self.get_calories_by_name(ing)
            if per100 is None:
                return {"needs_clarification": True, "message": "Ingredient not found."}
            cal = per100 * qty_grams / 100.0
            return {
                "needs_clarification": False,
                "dish": ing,
                "ingredients": [{"name": ing, "weight_g": qty_grams, "calories": round(cal,2)}],
                "total_calories": round(cal,2),
                "notes": []
            }

        dish = match.found_dish
        if not dish:
            return {"needs_clarification": True, "message": "Dish not found."}
        
        ingredients = []
        notes = []
        text = match.text.lower()

        for ing in dish["ingredients"]:
            name = ing.get("name", "").lower()
            weight = float(ing.get("weight_g", 0))
            if any(k in text for k in ["without", "bala", "بدون", "no"]) and name in text:
                notes.append(f"Removed {name}")
                continue
            
            # Get calories
            per100 = None
            if ing.get("usda_fdc_id"):
                per100 = self.get_calories_by_id(ing["usda_fdc_id"])
            if per100 is None:
                per100 = self.get_calories_by_name(name)
            
            cal = (per100 or 0) * weight / 100.0
            ingredients.append({"name": name, "weight_g": weight, "calories": round(cal,2)})

        # Handle additions
        for q in match.quantities:
            if "tomato" in text:
                w = to_grams("tomato", q["qty"], q["unit"])
                per100 = self.get_calories_by_name("tomato") or 0
                ingredients.append({"name": "tomato", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g tomato")
            if "olive oil" in text or "زيت" in text:
                w = to_grams("olive oil", q["qty"], q["unit"])
                per100 = self.get_calories_by_name("olive oil") or 0
                ingredients.append({"name": "olive oil", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g olive oil")

        total = round(sum(i["calories"] for i in ingredients), 2)
        return {
            "needs_clarification": False,
            "dish": dish["dish_name"],
            "ingredients": ingredients,
            "total_calories": total,
            "notes": notes
        }