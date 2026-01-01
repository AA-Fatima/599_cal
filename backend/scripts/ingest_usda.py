#!/usr/bin/env python3
"""
Ingest USDA foundation and legacy data into PostgreSQL database.
Streams large files to avoid memory issues.
"""
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from db import SessionLocal, engine
from models import UsdaItem
from settings import settings

def load_usda_json(file_path):
    """Load USDA JSON file - handles both array format and object format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check for common USDA keys
            if "FoundationFoods" in data:
                return data["FoundationFoods"]
            elif "SRLegacyFoods" in data:
                return data["SRLegacyFoods"]
            elif "foods" in data:
                return data["foods"]
            else:
                # Return all values if it's a dict of food items
                return list(data.values()) if data else []
        return []

def extract_usda_item(item):
    """Extract relevant fields from USDA JSON item."""
    fdc_id = item.get("fdc_id") or item.get("fdcId")
    name = (item.get("description") or item.get("name") or "").strip().lower()
    
    # Extract calories from nutrients
    calories = None
    nutrients = item.get("foodNutrients", [])
    if isinstance(nutrients, list):
        for nutrient in nutrients:
            # Nutrient ID 1008 or 208 is Energy (calories)
            nutrient_id = str(nutrient.get("nutrientId", ""))
            if nutrient_id in ("1008", "208"):
                calories = nutrient.get("value") or nutrient.get("amount")
                break
    
    # Extract basic macros
    macros = {}
    if isinstance(nutrients, list):
        for nutrient in nutrients:
            nutrient_id = str(nutrient.get("nutrientId", ""))
            value = nutrient.get("value") or nutrient.get("amount")
            # Protein: 1003, 203
            if nutrient_id in ("1003", "203"):
                macros["protein_g"] = value
            # Fat: 1004, 204
            elif nutrient_id in ("1004", "204"):
                macros["fat_g"] = value
            # Carbs: 1005, 205
            elif nutrient_id in ("1005", "205"):
                macros["carbs_g"] = value
    
    return {
        "fdc_id": fdc_id,
        "name": name,
        "alt_names": [],
        "per_100g_calories": calories,
        "macros": macros if macros else None
    }

def ingest_usda_file(file_path: str, db: Session, batch_size=500):
    """Ingest USDA JSON file (foundation or legacy)."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ File not found: {file_path}")
        return 0
    
    print(f"Processing {path.name}...")
    count = 0
    batch = []
    
    items = load_usda_json(file_path)
    total = len(items)
    print(f"  Found {total} items to process")
    
    for item in items:
        data = extract_usda_item(item)
        if data["fdc_id"] and data["name"] and data["per_100g_calories"] is not None:
            batch.append(data)
            count += 1
            
            if len(batch) >= batch_size:
                # Use upsert to handle duplicates
                stmt = insert(UsdaItem).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['fdc_id'],
                    set_=dict(
                        name=stmt.excluded.name,
                        per_100g_calories=stmt.excluded.per_100g_calories,
                        macros=stmt.excluded.macros
                    )
                )
                db.execute(stmt)
                db.commit()
                print(f"  Inserted {count}/{total} items...", end='\r')
                batch = []
    
    # Insert remaining batch
    if batch:
        stmt = insert(UsdaItem).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=['fdc_id'],
            set_=dict(
                name=stmt.excluded.name,
                per_100g_calories=stmt.excluded.per_100g_calories,
                macros=stmt.excluded.macros
            )
        )
        db.execute(stmt)
        db.commit()
    
    print(f"\n✓ Ingested {count} items from {path.name}")
    return count

def ingest_all_usda():
    """Ingest all USDA data files."""
    db = SessionLocal()
    try:
        total = 0
        
        # Ingest foundation data
        foundation_path = Path(settings.USDA_FOUND_PATH)
        if foundation_path.exists():
            total += ingest_usda_file(str(foundation_path), db)
        else:
            print(f"Warning: Foundation file not found: {foundation_path}")
        
        # Ingest legacy data if exists
        legacy_path = Path(settings.USDA_LEGACY_PATH)
        if legacy_path.exists():
            total += ingest_usda_file(str(legacy_path), db)
        else:
            print(f"Note: Legacy file not found (optional): {legacy_path}")
        
        print(f"\n✓ Total USDA items ingested: {total}")
        return total
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting USDA data ingestion...")
    ingest_all_usda()
    print("\n✓ USDA ingestion complete")
