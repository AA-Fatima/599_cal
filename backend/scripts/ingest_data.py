#!/usr/bin/env python3
"""
Ingestion script for USDA and dishes data into PostgreSQL.
Loads USDA foundation, SR legacy (if present), and dishes from Excel.
Creates tables with pg_trgm indexes for efficient fuzzy search.
"""
import json
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import engine, Base, SessionLocal
from models import UsdaItem, Dish, DishIngredient
from settings import settings


def enable_pg_trgm(session: Session):
    """Enable pg_trgm extension for fuzzy search."""
    try:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        session.commit()
        print("✓ pg_trgm extension enabled")
    except Exception as e:
        print(f"Warning: Could not enable pg_trgm: {e}")
        session.rollback()


def create_indexes(session: Session):
    """Create pg_trgm indexes on name fields."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_usda_name_trgm ON usda_items USING gin (name gin_trgm_ops);",
        "CREATE INDEX IF NOT EXISTS idx_dish_name_trgm ON dishes USING gin (dish_name gin_trgm_ops);",
        "CREATE INDEX IF NOT EXISTS idx_dish_ing_name_trgm ON dish_ingredients USING gin (ingredient_name gin_trgm_ops);"
    ]
    for idx_sql in indexes:
        try:
            session.execute(text(idx_sql))
            print(f"✓ Created index: {idx_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"Warning: Could not create index: {e}")
    session.commit()


def load_usda_json(path: str):
    """Load USDA JSON data (foundation or SR legacy format)."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for item in data:
        fdc_id = item.get('fdc_id') or item.get('fdcId')
        name = (item.get('description') or item.get('name') or '').strip().lower()
        
        # Extract calories (nutrient ID 1008 or 208)
        calories = None
        macros = {}
        for nutrient in item.get('foodNutrients', []):
            nutrient_id = str(nutrient.get('nutrientId', ''))
            value = nutrient.get('value')
            
            if nutrient_id in ('1008', '208'):  # Energy
                calories = value
            elif nutrient_id == '1003':  # Protein
                macros['protein'] = value
            elif nutrient_id == '1004':  # Fat
                macros['fat'] = value
            elif nutrient_id == '1005':  # Carbs
                macros['carbs'] = value
        
        if fdc_id and name and calories is not None:
            items.append({
                'fdc_id': int(fdc_id),
                'name': name,
                'alt_names': None,
                'per_100g_calories': float(calories),
                'macros': macros if macros else None
            })
    
    return items


def ingest_usda(session: Session):
    """Ingest USDA foundation and SR legacy data."""
    print("\n=== Ingesting USDA Data ===")
    
    # Load foundation
    foundation_path = Path(settings.USDA_FOUND_PATH)
    if foundation_path.exists():
        print(f"Loading {foundation_path}...")
        items = load_usda_json(str(foundation_path))
        print(f"  Found {len(items)} items")
        
        # Batch insert
        session.bulk_insert_mappings(UsdaItem, items)
        session.commit()
        print(f"✓ Inserted {len(items)} foundation items")
    else:
        print(f"✗ Foundation file not found: {foundation_path}")
    
    # Load SR legacy (optional)
    legacy_path = Path(settings.USDA_LEGACY_PATH)
    if legacy_path.exists():
        print(f"Loading {legacy_path}...")
        items = load_usda_json(str(legacy_path))
        print(f"  Found {len(items)} items")
        
        # Batch insert
        session.bulk_insert_mappings(UsdaItem, items)
        session.commit()
        print(f"✓ Inserted {len(items)} SR legacy items")
    else:
        print(f"ℹ SR legacy file not found (optional): {legacy_path}")


def ingest_dishes(session: Session):
    """Ingest dishes and ingredients from Excel."""
    print("\n=== Ingesting Dishes Data ===")
    
    xlsx_path = Path(settings.DISHES_XLSX_PATH)
    if not xlsx_path.exists():
        print(f"✗ Dishes file not found: {xlsx_path}")
        return
    
    print(f"Loading {xlsx_path}...")
    df = pd.read_excel(xlsx_path)
    print(f"  Found {len(df)} dishes")
    
    for _, row in df.iterrows():
        dish_id = int(row['dish_id'])
        dish_name = str(row['dish name']).strip().lower()
        country = str(row.get('Country', '')).strip()
        date_accessed = str(row.get('date_accessed', '')).strip()
        
        # Insert dish
        dish = Dish(
            dish_id=dish_id,
            dish_name=dish_name,
            country=country,
            date_accessed=date_accessed
        )
        session.merge(dish)
        
        # Parse and insert ingredients
        ingredients_json = row.get('ingredients', '[]')
        try:
            ingredients = json.loads(ingredients_json) if isinstance(ingredients_json, str) else []
        except:
            ingredients = []
        
        for ing in ingredients:
            if isinstance(ing, dict):
                ingredient = DishIngredient(
                    dish_id=dish_id,
                    usda_fdc_id=ing.get('usda_fdc_id'),
                    ingredient_name=str(ing.get('name', '')).strip().lower(),
                    default_weight_g=float(ing.get('weight_g', 0))
                )
                session.add(ingredient)
    
    session.commit()
    print(f"✓ Inserted {len(df)} dishes with ingredients")


def main():
    """Main ingestion flow."""
    print("=" * 60)
    print("USDA & Dishes Data Ingestion")
    print("=" * 60)
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    session = SessionLocal()
    try:
        # Enable pg_trgm
        enable_pg_trgm(session)
        
        # Clear existing data (optional - comment out to preserve)
        print("\nClearing existing data...")
        session.query(DishIngredient).delete()
        session.query(Dish).delete()
        session.query(UsdaItem).delete()
        session.commit()
        print("✓ Existing data cleared")
        
        # Ingest data
        ingest_usda(session)
        ingest_dishes(session)
        
        # Create indexes
        print("\n=== Creating Indexes ===")
        create_indexes(session)
        
        # Summary
        usda_count = session.query(UsdaItem).count()
        dish_count = session.query(Dish).count()
        ing_count = session.query(DishIngredient).count()
        
        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"USDA Items:        {usda_count}")
        print(f"Dishes:            {dish_count}")
        print(f"Dish Ingredients:  {ing_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during ingestion: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
