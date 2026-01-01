#!/usr/bin/env python3
"""
Initialize database schema and enable pg_trgm extension for fuzzy search.
"""
from sqlalchemy import text
from db import engine, Base
from models import UsdaItem, Dish, DishIngredient, Synonym, UnitConversion, MissingDish

def init_db():
    """Create all tables and enable pg_trgm extension."""
    # Enable pg_trgm extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            conn.commit()
            print("✓ pg_trgm extension enabled")
        except Exception as e:
            print(f"Warning: Could not enable pg_trgm: {e}")
            conn.rollback()
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("✓ Database tables created")
    
    # Create GIN indexes for trigram search
    with engine.connect() as conn:
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_usda_items_name_trgm ON usda_items USING gin(name gin_trgm_ops);"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_dishes_name_trgm ON dishes USING gin(dish_name gin_trgm_ops);"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_dish_ingredients_name_trgm ON dish_ingredients USING gin(ingredient_name gin_trgm_ops);"
            ))
            conn.commit()
            print("✓ Trigram indexes created")
        except Exception as e:
            print(f"Warning: Could not create trigram indexes: {e}")
            conn.rollback()

if __name__ == "__main__":
    init_db()
    print("\n✓ Database initialization complete")
