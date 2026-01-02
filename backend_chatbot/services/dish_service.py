import pandas as pd
import json
from typing import Optional, Dict, List
from models.schemas import ChatResponse, IngredientDetail, Totals, GPTResponse
from services.usda_lookup import UsdaLookup

class DishService:
    def __init__(self, usda_lookup: UsdaLookup, dishes_path: str):
        self.usda_lookup = usda_lookup
        self.dishes = self._load_dishes(dishes_path)
        self.dish_by_name = {d["dish_name"].lower(): d for d in self.dishes}
    
    def _load_dishes(self, path: str) -> List[Dict]:
        """Load dishes from Excel file"""
        df = pd.read_excel(path)
        dishes = []
        
        for _, row in df.iterrows():
            ingredients = []
            try:
                ingredients = json.loads(row["ingredients"])
            except Exception:
                pass
            
            dishes.append({
                "dish_id": int(row["dish_id"]),
                "dish_name": str(row["dish name"]).strip(),
                "country": row.get("Country", row.get("country", "")),
                "weight_g": float(row.get("weight (g)", 0)),
                "calories": float(row.get("calories", 0)),
                "ingredients": ingredients
            })
        
        return dishes
    
    def find_dish_by_name(self, dish_name: str) -> Optional[Dict]:
        """Find dish by name (case-insensitive)"""
        return self.dish_by_name.get(dish_name.lower())
    
    def get_all_dishes(self) -> List[Dict]:
        """Get all dishes"""
        return self.dishes
    
    def calculate_nutrition(self, gpt_response: GPTResponse) -> ChatResponse:
        """
        Calculate nutrition based on GPT response
        Steps:
        1. Look for dish in dataset by name
        2. If found, use its ingredients; otherwise use GPT ingredients
        3. Apply modifications (remove/add)
        4. Calculate totals
        """
        food_item = gpt_response.food_item
        notes = []
        
        # Try to find dish in dataset
        dish = self.find_dish_by_name(food_item)
        
        if dish:
            # Use dish ingredients from dataset
            base_ingredients = dish["ingredients"]
            notes.append(f"Found '{food_item}' in database")
        else:
            # Use GPT suggested ingredients
            base_ingredients = [
                {"name": ing, "weight_g": 100}  # Default 100g per ingredient
                for ing in gpt_response.ingredients
            ]
            notes.append(f"'{food_item}' not in database, using AI suggestions")
        
        # Build ingredient list with modifications
        ingredients_detail = []
        
        # Process base ingredients (excluding removed ones)
        for ing in base_ingredients:
            ing_name = ing.get("name", "").lower()
            
            # Check if this ingredient should be removed
            should_remove = False
            for remove_item in gpt_response.modifications.remove:
                if remove_item.lower() in ing_name or ing_name in remove_item.lower():
                    should_remove = True
                    notes.append(f"Removed: {ing_name}")
                    break
            
            if should_remove:
                continue
            
            # Calculate nutrition for this ingredient
            weight_g = float(ing.get("weight_g", 100))
            usda_item = None
            
            # Try lookup by FDC ID first if available
            if "usda_fdc_id" in ing:
                usda_item = self.usda_lookup.find_by_id(ing["usda_fdc_id"])
            
            # Fallback to name lookup
            if not usda_item:
                usda_item = self.usda_lookup.find_by_name(ing_name)
            
            if usda_item:
                multiplier = weight_g / 100.0
                ingredients_detail.append(IngredientDetail(
                    name=usda_item["name"],
                    weight_g=round(weight_g, 1),
                    calories=round(usda_item["per_100g_calories"] * multiplier, 1),
                    protein_g=round(usda_item["per_100g_protein"] * multiplier, 1),
                    fat_g=round(usda_item["per_100g_fat"] * multiplier, 1),
                    carbs_g=round(usda_item["per_100g_carbs"] * multiplier, 1)
                ))
        
        # Process added ingredients
        for add_item in gpt_response.modifications.add:
            usda_item = self.usda_lookup.find_by_name(add_item)
            
            if usda_item:
                # Default to 50g for added items
                weight_g = 50.0
                multiplier = weight_g / 100.0
                
                ingredients_detail.append(IngredientDetail(
                    name=usda_item["name"],
                    weight_g=round(weight_g, 1),
                    calories=round(usda_item["per_100g_calories"] * multiplier, 1),
                    protein_g=round(usda_item["per_100g_protein"] * multiplier, 1),
                    fat_g=round(usda_item["per_100g_fat"] * multiplier, 1),
                    carbs_g=round(usda_item["per_100g_carbs"] * multiplier, 1)
                ))
                notes.append(f"Added: {add_item} ({weight_g}g)")
        
        # Calculate totals
        totals = Totals(
            weight_g=round(sum(i.weight_g for i in ingredients_detail), 1),
            calories=round(sum(i.calories for i in ingredients_detail), 1),
            protein_g=round(sum(i.protein_g for i in ingredients_detail), 1),
            fat_g=round(sum(i.fat_g for i in ingredients_detail), 1),
            carbs_g=round(sum(i.carbs_g for i in ingredients_detail), 1)
        )
        
        return ChatResponse(
            food_item=food_item,
            ingredients=ingredients_detail,
            totals=totals,
            notes=notes
        )
    
    def add_dish(self, dish_name: str, country: str, ingredients: List[Dict]) -> Dict:
        """Add a new dish to the dataset (in-memory for now)"""
        # Generate new dish ID
        max_id = max([d["dish_id"] for d in self.dishes], default=1000000)
        new_id = max_id + 1
        
        # Calculate total weight and calories
        total_weight = sum(float(ing["weight_g"]) for ing in ingredients)
        total_calories = 0
        
        ingredient_details = []
        for ing in ingredients:
            usda_item = self.usda_lookup.find_by_name(ing["usda_name"])
            if usda_item:
                weight_g = float(ing["weight_g"])
                calories = usda_item["per_100g_calories"] * weight_g / 100.0
                total_calories += calories
                
                ingredient_details.append({
                    "usda_fdc_id": usda_item["fdc_id"],
                    "name": usda_item["name"],
                    "weight_g": weight_g,
                    "calories": round(calories, 2)
                })
        
        new_dish = {
            "dish_id": new_id,
            "dish_name": dish_name,
            "country": country,
            "weight_g": round(total_weight, 2),
            "calories": round(total_calories, 2),
            "ingredients": ingredient_details
        }
        
        # Add to in-memory list
        self.dishes.append(new_dish)
        self.dish_by_name[dish_name.lower()] = new_dish
        
        return new_dish
