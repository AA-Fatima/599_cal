#!/usr/bin/env python3
"""
Verification script to test key components before full deployment.
Run this to check if services are properly configured.
"""
import sys
from pathlib import Path

print("=" * 60)
print("Calorie Chatbot - Component Verification")
print("=" * 60)

# Test 1: Import basic modules
print("\n[1/6] Testing basic imports...")
try:
    from sqlalchemy import create_engine
    from fastapi import FastAPI
    import redis
    print("  ✓ Core dependencies available")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    sys.exit(1)

# Test 2: Check data files
print("\n[2/6] Checking data files...")
data_dir = Path("data")
files = {
    "USDA Foundation": data_dir / "USDA_foundation.json",
    "Dishes": data_dir / "dishes.xlsx",
}
for name, path in files.items():
    if path.exists():
        size = path.stat().st_size / 1024 / 1024  # MB
        print(f"  ✓ {name}: {path.name} ({size:.2f} MB)")
    else:
        print(f"  ✗ {name}: {path.name} NOT FOUND")

legacy_path = data_dir / "USDA_sr_legacy.json"
if legacy_path.exists():
    size = legacy_path.stat().st_size / 1024 / 1024
    print(f"  ✓ USDA Legacy (optional): {legacy_path.name} ({size:.2f} MB)")
else:
    print(f"  ℹ USDA Legacy (optional): Not present - will use foundation only")

# Test 3: Check models directory
print("\n[3/6] Checking ML models...")
models_dir = Path("models")
model_files = {
    "Intent Model": models_dir / "intent.joblib",
    "NER HF Model": models_dir / "ner_hf",
}
for name, path in model_files.items():
    if path.exists():
        print(f"  ✓ {name}: Found")
    else:
        print(f"  ℹ {name}: Not found - will use fallback")

# Test 4: Validate Python files syntax
print("\n[4/6] Validating Python syntax...")
py_files = [
    "main.py",
    "models.py",
    "db.py",
    "settings.py",
]
all_valid = True
for file in py_files:
    try:
        with open(file, 'r') as f:
            compile(f.read(), file, 'exec')
        print(f"  ✓ {file}")
    except SyntaxError as e:
        print(f"  ✗ {file}: {e}")
        all_valid = False

if not all_valid:
    print("\n  ✗ Syntax errors found!")
    sys.exit(1)

# Test 5: Check services
print("\n[5/6] Checking service files...")
services_dir = Path("services")
service_files = list(services_dir.glob("*.py"))
print(f"  ✓ Found {len(service_files)} service files")

# Test 6: Check scripts
print("\n[6/6] Checking ingestion scripts...")
scripts_dir = Path("scripts")
script_files = [
    "init_db.py",
    "ingest_usda.py",
    "ingest_dishes.py",
    "populate_reference_data.py",
    "ingest_all.py",
]
for file in script_files:
    path = scripts_dir / file
    if path.exists():
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file}: NOT FOUND")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)

print("\nNext steps:")
print("  1. Start services: docker-compose up -d")
print("  2. Initialize DB: docker-compose exec backend python scripts/init_db.py")
print("  3. Ingest data: docker-compose exec backend python scripts/ingest_all.py")
print("  4. Access frontend: http://localhost:4200")
print("\nFor local development:")
print("  Backend: uvicorn main:app --reload")
print("  Frontend: cd frontend && npm start")
