from sqlalchemy import func, text
from db import SessionLocal
from models import Dish, DishIngredient
from services.unit_map import to_grams
from services.usda_lookup import UsdaLookup

class DishService:
    def __init__(self):
        self.usda_lookup = UsdaLookup()
        self.db = None
    
    def get_db(self):
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db
    
    def find_dish_by_name(self, name: str):
        """Find dish by name using pg_trgm or exact match."""
        name = name.lower().strip()
        db = self.get_db()
        
        # Try exact match first
        dish = db.query(Dish).filter(func.lower(Dish.dish_name) == name).first()
        if dish:
            return dish
        
        # Try pg_trgm similarity search
        try:
            query = text("""
                SELECT dish_id, dish_name, country, date_accessed, similarity(dish_name, :name) as sim
                FROM dishes
                WHERE similarity(dish_name, :name) > 0.3
                ORDER BY sim DESC
                LIMIT 1
            """)
            result = db.execute(query, {"name": name}).first()
            if result:
                dish = db.query(Dish).filter(Dish.dish_id == result[0]).first()
                return dish
        except Exception as e:
            print(f"Warning: pg_trgm query failed: {e}")
        
        return None
    
    def get_dish_ingredients(self, dish_id: int):
        """Get all ingredients for a dish."""
        db = self.get_db()
        return db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id).all()

    def compute(self, match):
        """Compute calories for a dish or single ingredient."""
        if match.single_ingredient and not match.found_dish:
            ing = match.single_ingredient.lower()
            qty_grams = 100.0
            if match.quantities:
                q = match.quantities[0]
                qty_grams = to_grams(ing, q["qty"], q["unit"])
            per100 = self.usda_lookup.calories_by_name(ing)
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
        
        # Get ingredients from database
        dish_ingredients = self.get_dish_ingredients(dish.dish_id)
        
        ingredients = []
        notes = []
        text = match.text.lower()

        # Process each ingredient
        for ing_row in dish_ingredients:
            name = ing_row.ingredient_name.lower()
            weight = float(ing_row.default_weight_g or 0)
            
            # Check for removal modifiers
            if any(k in text for k in ["without", "bala", "بدون", "no"]) and name in text:
                notes.append(f"Removed {name}")
                continue
            
            # Get calories
            if ing_row.usda_fdc_id:
                per100 = self.usda_lookup.calories_by_id(ing_row.usda_fdc_id)
            else:
                per100 = self.usda_lookup.calories_by_name(name)
            
            cal = (per100 or 0) * weight / 100.0
            ingredients.append({"name": name, "weight_g": weight, "calories": round(cal,2)})

        # Handle additions from quantities
        for q in match.quantities:
            if "tomato" in text:
                w = to_grams("tomato", q["qty"], q["unit"])
                per100 = self.usda_lookup.calories_by_name("tomato") or 0
                ingredients.append({"name": "tomato", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g tomato")
            if "olive oil" in text or "زيت" in text:
                w = to_grams("olive oil", q["qty"], q["unit"])
                per100 = self.usda_lookup.calories_by_name("olive oil") or 0
                ingredients.append({"name": "olive oil", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g olive oil")

        total = round(sum(i["calories"] for i in ingredients), 2)
        return {
            "needs_clarification": False,
            "dish": dish.dish_name,
            "ingredients": ingredients,
            "total_calories": total,
            "notes": notes
        }