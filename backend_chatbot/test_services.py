#!/usr/bin/env python3
"""
Test script for backend_chatbot
Tests the fallback mechanisms without requiring OpenAI API key
"""

import sys
sys.path.insert(0, '.')

from services.usda_lookup import UsdaLookup
from services.dish_service import DishService
from services.fallback_service import FallbackService
from models.schemas import GPTResponse, Modifications

print("=" * 60)
print("Testing Backend Chatbot Services")
print("=" * 60)

# Test 1: USDA Lookup
print("\n1. Testing USDA Lookup...")
usda = UsdaLookup('data/USDA_foundation.json')
print(f"   ✓ Loaded {len(usda.items)} USDA items")

# Search test
results = usda.search('chicken', limit=3)
print(f"   ✓ Search for 'chicken' returned {len(results)} results")
if results:
    print(f"     First result: {results[0]['name']}")

# Test 2: Dish Service
print("\n2. Testing Dish Service...")
dish_service = DishService(usda, 'data/dishes.xlsx')
print(f"   ✓ Loaded {len(dish_service.dishes)} dishes")

# Find dish test
dish = dish_service.find_dish_by_name('Fajita')
if dish:
    print(f"   ✓ Found dish: {dish['dish_name']} ({dish['country']})")
    print(f"     Ingredients: {len(dish['ingredients'])}")
else:
    print("   ✗ Could not find 'Fajita'")

# Test 3: Fallback Service
print("\n3. Testing Fallback Service...")
dish_names = [d['dish_name'] for d in dish_service.dishes]
fallback = FallbackService(dish_names)

# Test fuzzy match
result = fallback.fuzzy_match_dish("i want fajta")
if result:
    print(f"   ✓ Fuzzy match for 'i want fajta': {result.food_item}")
else:
    print("   ✗ No fuzzy match found")

# Test simple extraction
result = fallback.simple_entity_extraction("how many calories in chicken")
if result:
    print(f"   ✓ Simple extraction: {result.food_item}")
else:
    print("   ✗ No extraction")

# Test 4: Calculate Nutrition
print("\n4. Testing Nutrition Calculation...")
gpt_mock = GPTResponse(
    food_item="Fajita",
    modifications=Modifications(remove=["french fries"], add=[]),
    ingredients=[]
)

try:
    response = dish_service.calculate_nutrition(gpt_mock)
    print(f"   ✓ Calculated nutrition for {response.food_item}")
    print(f"     Total calories: {response.totals.calories} kcal")
    print(f"     Total protein: {response.totals.protein_g}g")
    print(f"     Total fat: {response.totals.fat_g}g")
    print(f"     Total carbs: {response.totals.carbs_g}g")
    print(f"     Ingredients: {len(response.ingredients)}")
    if response.notes:
        print(f"     Notes: {', '.join(response.notes)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
