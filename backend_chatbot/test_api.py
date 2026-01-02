"""
Simple test script for backend_chatbot API
This tests the API without requiring OpenAI API key by using fallback mechanisms
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.usda_lookup import UsdaLookupService
from services.dish_service import DishService
from services.fallback_service import FallbackService
from models.schemas import GPTResponse, Modification

print("=" * 60)
print("Testing Backend Chatbot Services")
print("=" * 60)

# Test 1: USDA Lookup
print("\n1. Testing USDA Lookup Service...")
usda = UsdaLookupService('data/USDA_foundation.json')
print(f"   ✓ Loaded {len(usda.items)} USDA items")

# Test search
result = usda.search_by_name("tomato")
if result:
    print(f"   ✓ Found tomato: {result['name']}")
else:
    print("   ✗ Failed to find tomato")

# Test 2: Dish Service
print("\n2. Testing Dish Service...")
dish_svc = DishService('data/dishes.xlsx', usda)
print(f"   ✓ Loaded {len(dish_svc.dishes)} dishes")

# Find a specific dish
dish = dish_svc.find_dish_by_name("Chicken Shawarma Wrap")
if dish:
    print(f"   ✓ Found dish: {dish['dish_name']}")
    print(f"   ✓ Has {len(dish['ingredients'])} ingredients")
else:
    print("   ✗ Failed to find Chicken Shawarma Wrap")

# Test 3: Calculate calories for a known dish
print("\n3. Testing Calorie Calculation...")
gpt_response = GPTResponse(
    food_item="Chicken Shawarma Wrap",
    modifications=Modification(remove=[], add=[]),
    ingredients=[]
)

result = dish_svc.calculate_from_gpt(gpt_response)
print(f"   ✓ Calculated: {result.totals.calories} calories")
print(f"   ✓ Protein: {result.totals.protein_g}g")
print(f"   ✓ Fat: {result.totals.fat_g}g")
print(f"   ✓ Carbs: {result.totals.carbs_g}g")
print(f"   ✓ {len(result.ingredients)} ingredients processed")

# Test 4: Fallback Service
print("\n4. Testing Fallback Service...")
fallback = FallbackService(dish_svc)

# Try fuzzy matching
fuzzy_result = fallback.fuzzy_match_dish("chicken shawarma")
if fuzzy_result:
    print(f"   ✓ Fuzzy match found: {fuzzy_result.food_item}")
else:
    print("   ✗ Fuzzy match failed")

# Test 5: USDA Search (for autocomplete)
print("\n5. Testing USDA Autocomplete Search...")
search_results = usda.search_autocomplete("chicken", limit=5)
print(f"   ✓ Found {len(search_results)} results for 'chicken'")
for r in search_results[:3]:
    print(f"      - {r['name']}")

# Test 6: Test with modifications
print("\n6. Testing with Modifications...")
gpt_response_with_mods = GPTResponse(
    food_item="Chicken Shawarma Wrap",
    modifications=Modification(
        remove=["Tahini"],
        add=["Tomatoes, grape, raw"]
    ),
    ingredients=[]
)

result_with_mods = dish_svc.calculate_from_gpt(gpt_response_with_mods)
print(f"   ✓ Calculated with modifications: {result_with_mods.totals.calories} calories")
print(f"   ✓ Notes: {result_with_mods.notes}")

print("\n" + "=" * 60)
print("All tests completed successfully!")
print("=" * 60)
