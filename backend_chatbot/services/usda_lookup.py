import json
from typing import Optional, Dict, List
from rapidfuzz import process, fuzz
from functools import lru_cache

class UsdaLookup:
    def __init__(self, usda_path: str):
        self.items = self._load_usda(usda_path)
        self.by_name = {item["name"].lower(): item for item in self.items}
        self.names = list(self.by_name.keys())
        self.by_id = {item["fdc_id"]: item for item in self.items}
    
    def _load_usda(self, path: str) -> List[Dict]:
        """Load USDA data and extract nutrients"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle both dict with 'FoundationFoods' key and direct list
        if isinstance(data, dict) and "FoundationFoods" in data:
            foods = data["FoundationFoods"]
        elif isinstance(data, list):
            foods = data
        else:
            foods = []
        
        items = []
        for food in foods:
            fdc_id = food.get("fdcId") or food.get("fdc_id")
            name = (food.get("description") or "").strip()
            
            if not fdc_id or not name:
                continue
            
            # Extract nutrients
            nutrients = {}
            for nutrient in food.get("foodNutrients", []):
                nutrient_info = nutrient.get("nutrient", {})
                nutrient_id = nutrient_info.get("id") or nutrient.get("nutrientId")
                amount = nutrient.get("amount") or nutrient.get("value")
                
                # Map nutrient IDs to our keys
                # 1008/208 = Energy (calories)
                # 1003/203 = Protein
                # 1004/204 = Total lipid (fat)
                # 1005/205 = Carbohydrate
                if str(nutrient_id) in ("1008", "208"):
                    nutrients["calories"] = amount
                elif str(nutrient_id) in ("1003", "203"):
                    nutrients["protein"] = amount
                elif str(nutrient_id) in ("1004", "204"):
                    nutrients["fat"] = amount
                elif str(nutrient_id) in ("1005", "205"):
                    nutrients["carbs"] = amount
            
            if "calories" in nutrients:
                items.append({
                    "fdc_id": fdc_id,
                    "name": name,
                    "per_100g_calories": nutrients.get("calories", 0),
                    "per_100g_protein": nutrients.get("protein", 0),
                    "per_100g_fat": nutrients.get("fat", 0),
                    "per_100g_carbs": nutrients.get("carbs", 0),
                })
        
        return items
    
    @lru_cache(maxsize=4096)
    def find_by_name(self, name: str) -> Optional[Dict]:
        """Find ingredient by exact or fuzzy name match"""
        name = name.lower().strip()
        
        # Try exact match first
        if name in self.by_name:
            return self.by_name[name]
        
        # Try fuzzy match
        match = process.extractOne(name, self.names, scorer=fuzz.WRatio, score_cutoff=80)
        if match:
            return self.by_name[match[0]]
        
        return None
    
    def find_by_id(self, fdc_id: int) -> Optional[Dict]:
        """Find ingredient by FDC ID"""
        return self.by_id.get(fdc_id)
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for ingredients by name (for autocomplete)"""
        query = query.lower().strip()
        if not query:
            return []
        
        matches = process.extract(query, self.names, scorer=fuzz.WRatio, limit=limit)
        results = []
        for match_name, score, _ in matches:
            if score > 60:
                item = self.by_name[match_name]
                results.append({
                    "fdc_id": item["fdc_id"],
                    "name": item["name"],
                    "score": score
                })
        
        return results
