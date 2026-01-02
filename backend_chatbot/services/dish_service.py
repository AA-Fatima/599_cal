import pandas as pd
import json
from typing import Dict, List, Optional
from models.schemas import ChatResponse, IngredientDetail, NutritionTotals, GPTResponse
from services.usda_lookup import UsdaLookupService

class DishService:
    def __init__(self, dishes_path: str, usda_lookup: UsdaLookupService):
        self.usda_lookup = usda_lookup
        self.dishes = self._load_dishes(dishes_path)
        self.dish_by_name = {}
        
        # Build index by dish name (lowercase for case-insensitive lookup)
        for dish in self.dishes:
            name_lower = dish["dish_name"].lower().strip()
            self.dish_by_name[name_lower] = dish
    
    def _load_dishes(self, xlsx_path: str) -> List[Dict]:
        """Load dishes from Excel file"""
        df = pd.read_excel(xlsx_path)
        dishes = []
        
        for _, row in df.iterrows():
            ingredients = []
            try:
                ingredients = json.loads(row["ingredients"])
            except Exception:
                pass
            
            dishes.append({
                "dish_id": int(row["dish_id"]) if "dish_id" in row else 0,
                "dish_name": str(row["dish name"]).strip(),
                "country": row.get("Country", ""),
                "ingredients": ingredients
            })
        
        return dishes
    
    def find_dish_by_name(self, name: str) -> Optional[Dict]:
        """Find dish by full name"""
        name_lower = name.lower().strip()
        return self.dish_by_name.get(name_lower)
    
    def calculate_from_gpt(self, gpt_response: GPTResponse, default_weight: float = 100.0) -> ChatResponse:
        """Calculate calories from GPT response"""
        # First, check if dish exists in dataset
        dish_data = self.find_dish_by_name(gpt_response.food_item)
        
        ingredients_list = []
        notes = []
        
        if dish_data:
            # Use pre-defined ingredients from dataset
            base_ingredients = dish_data["ingredients"]
            notes.append(f"Found '{gpt_response.food_item}' in database")
        else:
            # Use GPT-suggested ingredients
            base_ingredients = []
            for ing_name in gpt_response.ingredients:
                usda_item = self.usda_lookup.search_by_name(ing_name)
                if usda_item:
                    base_ingredients.append({
                        "name": usda_item["name"],
                        "usda_fdc_id": usda_item["fdc_id"],
                        "weight_g": default_weight
                    })
            notes.append(f"'{gpt_response.food_item}' not found in database, using GPT suggestions")
        
        # Process ingredients and apply modifications
        ingredients_to_use = []
        
        # Filter out removed ingredients
        for ing in base_ingredients:
            ing_name = ing.get("name", "").lower()
            
            # Check if this ingredient should be removed
            should_remove = False
            for remove_item in gpt_response.modifications.remove:
                if remove_item.lower() in ing_name or ing_name in remove_item.lower():
                    should_remove = True
                    notes.append(f"Removed: {ing.get('name', ing_name)}")
                    break
            
            if not should_remove:
                ingredients_to_use.append(ing)
        
        # Add additional ingredients
        for add_item in gpt_response.modifications.add:
            usda_item = self.usda_lookup.search_by_name(add_item)
            if usda_item:
                ingredients_to_use.append({
                    "name": usda_item["name"],
                    "usda_fdc_id": usda_item["fdc_id"],
                    "weight_g": default_weight
                })
                notes.append(f"Added: {usda_item['name']}")
        
        # Calculate nutritional values for each ingredient
        for ing in ingredients_to_use:
            fdc_id = ing.get("usda_fdc_id")
            weight_g = float(ing.get("weight_g", default_weight))
            
            # Get USDA data
            usda_item = None
            if fdc_id:
                usda_item = self.usda_lookup.get_by_id(fdc_id)
            
            if not usda_item:
                # Try searching by name
                usda_item = self.usda_lookup.search_by_name(ing.get("name", ""))
            
            if usda_item:
                # Calculate based on weight
                factor = weight_g / 100.0
                
                ingredient_detail = IngredientDetail(
                    usda_fdc_id=usda_item["fdc_id"],
                    name=usda_item["name"],
                    weight_g=round(weight_g, 1),
                    calories=round(usda_item["per_100g_calories"] * factor, 1),
                    protein_g=round(usda_item["per_100g_protein"] * factor, 1),
                    fat_g=round(usda_item["per_100g_fat"] * factor, 1),
                    carbs_g=round(usda_item["per_100g_carbs"] * factor, 1)
                )
                ingredients_list.append(ingredient_detail)
        
        # Calculate totals
        totals = NutritionTotals(
            weight_g=round(sum(ing.weight_g for ing in ingredients_list), 1),
            calories=round(sum(ing.calories for ing in ingredients_list), 1),
            protein_g=round(sum(ing.protein_g for ing in ingredients_list), 1),
            fat_g=round(sum(ing.fat_g for ing in ingredients_list), 1),
            carbs_g=round(sum(ing.carbs_g for ing in ingredients_list), 1)
        )
        
        return ChatResponse(
            food_item=gpt_response.food_item,
            ingredients=ingredients_list,
            totals=totals,
            notes=notes
        )
    
    def get_all_dishes(self) -> List[Dict]:
        """Get all dishes in dataset"""
        return self.dishes
    
    def add_dish(self, dish_name: str, country: str, ingredients: List[Dict]) -> Dict:
        """Add new dish to dataset (in-memory for now)"""
        new_dish = {
            "dish_id": len(self.dishes) + 1,
            "dish_name": dish_name,
            "country": country,
            "ingredients": ingredients
        }
        self.dishes.append(new_dish)
        self.dish_by_name[dish_name.lower().strip()] = new_dish
        return new_dish
