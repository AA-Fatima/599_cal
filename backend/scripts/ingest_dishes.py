#!/usr/bin/env python3
"""
Ingest dishes from Excel file into PostgreSQL database.
"""
import json
from pathlib import Path
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from db import SessionLocal
from models import Dish, DishIngredient
from settings import settings

def ingest_dishes():
    """Ingest dishes and their ingredients from Excel file."""
    xlsx_path = Path(settings.DISHES_XLSX_PATH)
    if not xlsx_path.exists():
        print(f"✗ Dishes file not found: {xlsx_path}")
        return 0
    
    print(f"Processing {xlsx_path.name}...")
    df = pd.read_excel(xlsx_path)
    
    db = SessionLocal()
    try:
        dish_count = 0
        ingredient_count = 0
        
        for _, row in df.iterrows():
            dish_id = int(row.get("dish_id", 0))
            dish_name = str(row.get("dish name", "")).strip().lower()
            country = str(row.get("Country", ""))
            date_accessed = str(row.get("date_accessed", ""))
            
            if not dish_id or not dish_name:
                continue
            
            # Insert or update dish
            dish_data = {
                "dish_id": dish_id,
                "dish_name": dish_name,
                "country": country,
                "date_accessed": date_accessed
            }
            
            stmt = insert(Dish).values(dish_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['dish_id'],
                set_=dict(
                    dish_name=stmt.excluded.dish_name,
                    country=stmt.excluded.country,
                    date_accessed=stmt.excluded.date_accessed
                )
            )
            db.execute(stmt)
            dish_count += 1
            
            # Parse ingredients JSON
            ingredients_raw = row.get("ingredients", "[]")
            try:
                if isinstance(ingredients_raw, str):
                    ingredients = json.loads(ingredients_raw)
                else:
                    ingredients = ingredients_raw if isinstance(ingredients_raw, list) else []
            except (json.JSONDecodeError, TypeError):
                ingredients = []
            
            # Insert ingredients
            for ing in ingredients:
                if isinstance(ing, dict):
                    ing_data = {
                        "dish_id": dish_id,
                        "usda_fdc_id": ing.get("usda_fdc_id"),
                        "ingredient_name": str(ing.get("name", "")).strip().lower(),
                        "default_weight_g": float(ing.get("weight_g", 0))
                    }
                    
                    if ing_data["ingredient_name"]:
                        # For ingredients, we don't have a unique constraint, so just insert
                        # First delete existing ingredients for this dish to avoid duplicates
                        # We'll do this once per dish
                        db.execute(stmt)
                        ingredient_count += 1
        
        # Actually, let's delete and re-insert ingredients for each dish to avoid duplicates
        # Better approach: delete all for each dish first
        for _, row in df.iterrows():
            dish_id = int(row.get("dish_id", 0))
            if not dish_id:
                continue
            
            # Delete existing ingredients
            db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id).delete()
        
        db.commit()
        
        # Now insert all ingredients
        ingredient_count = 0
        for _, row in df.iterrows():
            dish_id = int(row.get("dish_id", 0))
            if not dish_id:
                continue
            
            ingredients_raw = row.get("ingredients", "[]")
            try:
                if isinstance(ingredients_raw, str):
                    ingredients = json.loads(ingredients_raw)
                else:
                    ingredients = ingredients_raw if isinstance(ingredients_raw, list) else []
            except (json.JSONDecodeError, TypeError):
                ingredients = []
            
            for ing in ingredients:
                if isinstance(ing, dict):
                    ing_obj = DishIngredient(
                        dish_id=dish_id,
                        usda_fdc_id=ing.get("usda_fdc_id"),
                        ingredient_name=str(ing.get("name", "")).strip().lower(),
                        default_weight_g=float(ing.get("weight_g", 0))
                    )
                    if ing_obj.ingredient_name:
                        db.add(ing_obj)
                        ingredient_count += 1
        
        db.commit()
        
        print(f"✓ Ingested {dish_count} dishes")
        print(f"✓ Ingested {ingredient_count} ingredients")
        return dish_count
    
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting dishes data ingestion...")
    ingest_dishes()
    print("\n✓ Dishes ingestion complete")
