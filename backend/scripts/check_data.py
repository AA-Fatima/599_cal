#!/usr/bin/env python3
"""
Check if all required data files are present and valid.
"""
import json
from pathlib import Path
import pandas as pd


def check_file(path: Path, name: str, check_func=None):
    """Check if a file exists and is valid."""
    if not path.exists():
        print(f"✗ {name} not found at {path}")
        return False
    
    try:
        if check_func:
            check_func(path)
        print(f"✓ {name} found ({path.stat().st_size / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ {name} invalid: {e}")
        return False


def check_json(path: Path):
    """Check if JSON is valid."""
    with open(path) as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected JSON array")
        print(f"    → {len(data)} items")


def check_excel(path: Path):
    """Check if Excel is valid."""
    df = pd.read_excel(path)
    print(f"    → {len(df)} rows, {len(df.columns)} columns")
    required_cols = ["dish_id", "dish name", "ingredients"]
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def main():
    print("=" * 60)
    print("Data Files Check")
    print("=" * 60)
    
    base = Path(__file__).parent.parent / "data"
    
    checks = [
        (base / "USDA_foundation.json", "USDA Foundation", check_json),
        (base / "USDA_sr_legacy.json", "USDA SR Legacy", check_json),
        (base / "dishes.xlsx", "Dishes Excel", check_excel),
    ]
    
    results = []
    for path, name, check_func in checks:
        results.append(check_file(path, name, check_func))
    
    print("=" * 60)
    if all(results):
        print("✓ All data files present and valid")
        return 0
    else:
        print("✗ Some data files are missing or invalid")
        return 1


if __name__ == '__main__':
    exit(main())
