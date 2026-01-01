#!/usr/bin/env python3
"""
Populate synonyms and unit conversions in database.
"""
from sqlalchemy.dialects.postgresql import insert
from db import SessionLocal
from models import Synonym, UnitConversion

# Expanded synonyms for Arabic/Franco/English variants
SYNONYMS_DATA = [
    # Fajita variants
    ("فاهيتا", "fajita"),
    ("فهيتا", "fajita"),
    ("fahita", "fajita"),
    ("faheta", "fajita"),
    ("fjita", "fajita"),
    ("فاجيتا", "fajita"),
    
    # Tabbouleh variants
    ("تبولة", "tabbouleh"),
    ("تبوله", "tabbouleh"),
    ("tabbouli", "tabbouleh"),
    ("tabbouleh", "tabbouleh"),
    ("taboule", "tabbouleh"),
    ("taboula", "tabbouleh"),
    ("تبولي", "tabbouleh"),
    
    # Fries/Potato variants
    ("بطاطا", "fries"),
    ("بطاطا مقلية", "fries"),
    ("بطاطس", "fries"),
    ("batata", "fries"),
    ("batatas", "fries"),
    ("fries", "fries"),
    ("french fries", "fries"),
    
    # Tomato variants
    ("بندورة", "tomato"),
    ("طماطم", "tomato"),
    ("بندوره", "tomato"),
    ("tamata", "tomato"),
    ("tomato", "tomato"),
    
    # Olive oil variants
    ("زيت زيتون", "olive oil"),
    ("زيت الزيتون", "olive oil"),
    ("zayt zaytoun", "olive oil"),
    ("olive oil", "olive oil"),
    
    # Rice variants
    ("رز", "rice"),
    ("ارز", "rice"),
    ("رُز", "rice"),
    ("riz", "rice"),
    ("roz", "rice"),
    ("rice", "rice"),
    
    # Chicken variants
    ("دجاج", "chicken"),
    ("فراخ", "chicken"),
    ("djej", "chicken"),
    ("dajaj", "chicken"),
    ("chicken", "chicken"),
    
    # Beef variants
    ("لحم", "beef"),
    ("لحمة", "beef"),
    ("lahme", "beef"),
    ("laham", "beef"),
    ("beef", "beef"),
    
    # Onion variants
    ("بصل", "onion"),
    ("بصله", "onion"),
    ("basal", "onion"),
    ("onion", "onion"),
    
    # Garlic variants
    ("ثوم", "garlic"),
    ("toum", "garlic"),
    ("thoum", "garlic"),
    ("garlic", "garlic"),
    
    # Lemon variants
    ("ليمون", "lemon"),
    ("حامض", "lemon"),
    ("laymoun", "lemon"),
    ("lemon", "lemon"),
    
    # Yogurt variants
    ("لبن", "yogurt"),
    ("لبنة", "yogurt"),
    ("laban", "yogurt"),
    ("labneh", "yogurt"),
    ("yogurt", "yogurt"),
]

# Unit conversions with per-ingredient overrides
UNIT_CONVERSIONS_DATA = [
    # Generic conversions
    ("generic", "g", 1.0),
    ("generic", "gram", 1.0),
    ("generic", "grams", 1.0),
    ("generic", "kg", 1000.0),
    ("generic", "kilogram", 1000.0),
    ("generic", "tbsp", 15.0),
    ("generic", "tablespoon", 15.0),
    ("generic", "tsp", 5.0),
    ("generic", "teaspoon", 5.0),
    ("generic", "piece", 50.0),
    ("generic", "حبة", 50.0),
    ("generic", "حبه", 50.0),
    ("generic", "cup", 240.0),
    ("generic", "كوب", 240.0),
    
    # Olive oil specific
    ("olive oil", "tbsp", 13.5),
    ("olive oil", "tablespoon", 13.5),
    ("olive oil", "tsp", 4.5),
    ("olive oil", "teaspoon", 4.5),
    ("olive oil", "ملعقة كبيرة", 13.5),
    ("olive oil", "ملعقه كبيره", 13.5),
    ("olive oil", "م ك", 13.5),
    ("olive oil", "ملعقة صغيرة", 4.5),
    ("olive oil", "م ص", 4.5),
    
    # Tomato specific
    ("tomato", "piece", 123.0),
    ("tomato", "حبة", 123.0),
    ("tomato", "حبه", 123.0),
    ("tomato", "small", 100.0),
    ("tomato", "medium", 123.0),
    ("tomato", "large", 180.0),
    
    # Apple specific
    ("apple", "piece", 182.0),
    ("apple", "حبة", 182.0),
    ("apple", "small", 150.0),
    ("apple", "medium", 182.0),
    ("apple", "large", 223.0),
    
    # Potato specific
    ("potato", "piece", 150.0),
    ("potato", "حبة", 150.0),
    ("potato", "small", 120.0),
    ("potato", "medium", 150.0),
    ("potato", "large", 200.0),
    
    # Onion specific
    ("onion", "piece", 110.0),
    ("onion", "حبة", 110.0),
    ("onion", "small", 70.0),
    ("onion", "medium", 110.0),
    ("onion", "large", 150.0),
    
    # Egg specific
    ("egg", "piece", 50.0),
    ("egg", "حبة", 50.0),
    ("egg", "small", 40.0),
    ("egg", "medium", 50.0),
    ("egg", "large", 56.0),
]

def populate_synonyms():
    """Populate synonyms table."""
    db = SessionLocal()
    try:
        count = 0
        for term, canonical in SYNONYMS_DATA:
            stmt = insert(Synonym).values(term=term, canonical=canonical)
            stmt = stmt.on_conflict_do_update(
                index_elements=['term'],
                set_=dict(canonical=stmt.excluded.canonical)
            )
            db.execute(stmt)
            count += 1
        
        db.commit()
        print(f"✓ Populated {count} synonyms")
        return count
    finally:
        db.close()

def populate_unit_conversions():
    """Populate unit conversions table."""
    db = SessionLocal()
    try:
        count = 0
        for ingredient_group, unit, grams in UNIT_CONVERSIONS_DATA:
            conversion = UnitConversion(
                ingredient_group=ingredient_group,
                unit=unit,
                grams=grams
            )
            db.merge(conversion)
            count += 1
        
        db.commit()
        print(f"✓ Populated {count} unit conversions")
        return count
    finally:
        db.close()

if __name__ == "__main__":
    print("Populating reference data...")
    populate_synonyms()
    populate_unit_conversions()
    print("\n✓ Reference data population complete")
