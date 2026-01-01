#!/usr/bin/env python3
"""
Master ingestion script that runs all data loading steps in order.
Run this after initializing the database schema.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("=" * 60)
    print("Starting full data ingestion pipeline")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/4] Initializing database schema...")
    try:
        from scripts.init_db import init_db
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    
    # Step 2: Ingest USDA data
    print("\n[2/4] Ingesting USDA food data...")
    try:
        from scripts.ingest_usda import ingest_all_usda
        ingest_all_usda()
    except Exception as e:
        print(f"Error ingesting USDA data: {e}")
        return 1
    
    # Step 3: Ingest dishes
    print("\n[3/4] Ingesting dishes data...")
    try:
        from scripts.ingest_dishes import ingest_dishes
        ingest_dishes()
    except Exception as e:
        print(f"Error ingesting dishes: {e}")
        return 1
    
    # Step 4: Populate reference data
    print("\n[4/4] Populating reference data...")
    try:
        from scripts.populate_reference_data import populate_synonyms, populate_unit_conversions
        populate_synonyms()
        populate_unit_conversions()
    except Exception as e:
        print(f"Error populating reference data: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("✓ Full data ingestion completed successfully!")
    print("=" * 60)
    print("\nYou can now start the application:")
    print("  uvicorn main:app --host 0.0.0.0 --port 8000")
    print("\nOr with Docker Compose:")
    print("  docker-compose up")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
