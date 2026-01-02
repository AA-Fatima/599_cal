#!/usr/bin/env python3
"""
Demo script showing how to interact with the backend_chatbot API
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def demo_chat(query):
    """Demo the chat endpoint"""
    print(f"Query: \"{query}\"")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFood Item: {data['food_item']}")
        print(f"\nIngredients ({len(data['ingredients'])}):")
        for ing in data['ingredients']:
            print(f"  • {ing['name']}")
            print(f"    Weight: {ing['weight_g']}g")
            print(f"    Calories: {ing['calories']} kcal")
            print(f"    Macros: P={ing['protein_g']}g, F={ing['fat_g']}g, C={ing['carbs_g']}g")
        
        print(f"\nTotals:")
        totals = data['totals']
        print(f"  Weight: {totals['weight_g']}g")
        print(f"  Calories: {totals['calories']} kcal")
        print(f"  Protein: {totals['protein_g']}g")
        print(f"  Fat: {totals['fat_g']}g")
        print(f"  Carbs: {totals['carbs_g']}g")
        
        if data.get('notes'):
            print(f"\nNotes:")
            for note in data['notes']:
                print(f"  - {note}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

def demo_search_usda(query):
    """Demo USDA ingredient search"""
    print(f"Searching for: \"{query}\"")
    
    response = requests.get(f"{BASE_URL}/usda/search?q={query}&limit=5")
    
    if response.status_code == 200:
        results = response.json()
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['name']}")
            print(f"     FDC ID: {result['fdc_id']}, Score: {result['score']:.1f}")
    else:
        print(f"Error: {response.status_code}")

def demo_list_dishes():
    """Demo listing all dishes"""
    response = requests.get(f"{BASE_URL}/dishes")
    
    if response.status_code == 200:
        dishes = response.json()
        print(f"Total dishes in database: {len(dishes)}")
        print("\nFirst 5 dishes:")
        for dish in dishes[:5]:
            print(f"  • {dish['dish_name']} ({dish['country']})")
            print(f"    {dish['calories']} kcal, {dish['weight_g']}g")
    else:
        print(f"Error: {response.status_code}")

def demo_add_dish():
    """Demo adding a new dish"""
    new_dish = {
        "dish_name": "Greek Salad",
        "country": "Greece",
        "ingredients": [
            {"usda_name": "Tomatoes, grape, raw", "weight_g": 150},
            {"usda_name": "Kale, raw", "weight_g": 50}
        ]
    }
    
    print("Adding new dish:")
    print(json.dumps(new_dish, indent=2))
    
    response = requests.post(f"{BASE_URL}/dishes", json=new_dish)
    
    if response.status_code == 200:
        dish = response.json()
        print(f"\n✓ Successfully added: {dish['dish_name']}")
        print(f"  ID: {dish['dish_id']}")
        print(f"  Calories: {dish['calories']} kcal")
        print(f"  Weight: {dish['weight_g']}g")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

def demo_missing_dishes():
    """Demo getting missing dishes"""
    response = requests.get(f"{BASE_URL}/missing-dishes")
    
    if response.status_code == 200:
        missing = response.json()
        print(f"Missing dishes logged: {len(missing)}")
        if missing:
            print("\nMost recent missing dishes:")
            for m in missing[-3:]:
                print(f"  • {m['dish_name']}")
                print(f"    Query: \"{m['user_query']}\"")
                print(f"    Suggested: {', '.join(m['gpt_suggested_ingredients'][:3])}")
                print(f"    Time: {m['timestamp']}")
    else:
        print(f"Error: {response.status_code}")

def main():
    print("=" * 60)
    print("  Backend Chatbot API Demo")
    print("=" * 60)
    print("\nMake sure the backend_chatbot is running on port 8001")
    print("Start it with: cd backend_chatbot && python main.py")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL[:-4]}/")
        if response.status_code != 200:
            print("\n❌ Cannot connect to backend_chatbot")
            print("   Make sure it's running on http://localhost:8001")
            return
        
        print("\n✓ Connected to backend_chatbot")
        
        # Demo 1: List dishes
        print_section("1. List All Dishes")
        demo_list_dishes()
        
        # Demo 2: Search USDA ingredients
        print_section("2. Search USDA Ingredients")
        demo_search_usda("chicken")
        
        # Demo 3: Chat queries
        print_section("3. Chat Query - Existing Dish")
        demo_chat("how many calories in fajita")
        
        print_section("4. Chat Query - With Modifications")
        demo_chat("fajita without french fries")
        
        # Demo 4: Add dish
        print_section("5. Add New Dish")
        demo_add_dish()
        
        # Demo 5: Missing dishes
        print_section("6. View Missing Dishes")
        demo_missing_dishes()
        
        print("\n" + "=" * 60)
        print("  Demo Complete!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend_chatbot")
        print("   Make sure it's running on http://localhost:8001")
        print("   Start it with: cd backend_chatbot && python main.py")

if __name__ == "__main__":
    main()
