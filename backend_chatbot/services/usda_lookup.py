import json
from typing import Optional, Dict, List
from rapidfuzz import process, fuzz

class UsdaLookupService:
    def __init__(self, usda_found_path: str):
        self.items = self._load_usda(usda_found_path)
        self.by_name = {}
        self.by_id = {}
        
        # Build indices for fast lookup
        for item in self.items:
            # Store with original case for exact match, and lowercase for fuzzy
            name_lower = item["name"].lower()
            self.by_name[name_lower] = item
            self.by_id[item["fdc_id"]] = item
        
        self.names = list(self.by_name.keys())
    
    def _load_usda(self, path: str) -> List[Dict]:
        """Load USDA foundation data and extract nutritional info"""
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        items = []
        for item in raw_data:
            fdc_id = item.get("fdcId") or item.get("fdc_id")
            # Keep original case for the name
            name = (item.get("description") or item.get("name") or "").strip()
            
            # Extract nutrients
            nutrients = {}
            for nutrient in item.get("foodNutrients", []):
                nutrient_id = str(nutrient.get("nutrientId") or nutrient.get("nutrient", {}).get("id", ""))
                value = nutrient.get("value") or nutrient.get("amount")
                
                # Map nutrient IDs to names
                if nutrient_id in ("1008", "208"):  # Energy (calories)
                    nutrients["calories"] = value
                elif nutrient_id in ("1003", "203"):  # Protein
                    nutrients["protein"] = value
                elif nutrient_id in ("1004", "204"):  # Fat
                    nutrients["fat"] = value
                elif nutrient_id in ("1005", "205"):  # Carbohydrates
                    nutrients["carbs"] = value
            
            if fdc_id and name and "calories" in nutrients:
                items.append({
                    "fdc_id": fdc_id,
                    "name": name,  # Keep original case
                    "per_100g_calories": nutrients.get("calories", 0),
                    "per_100g_protein": nutrients.get("protein", 0),
                    "per_100g_fat": nutrients.get("fat", 0),
                    "per_100g_carbs": nutrients.get("carbs", 0),
                })
        
        return items
    
    def search_by_name(self, name: str, threshold: int = 80) -> Optional[Dict]:
        """Search for ingredient by full name with fuzzy matching"""
        name_lower = name.lower().strip()
        
        # Try exact match first
        if name_lower in self.by_name:
            return self.by_name[name_lower]
        
        # Try fuzzy match
        match = process.extractOne(name_lower, self.names, scorer=fuzz.WRatio, score_cutoff=threshold)
        if match:
            return self.by_name[match[0]]
        
        return None
    
    def get_by_id(self, fdc_id: int) -> Optional[Dict]:
        """Get ingredient by FDC ID"""
        return self.by_id.get(fdc_id)
    
    def search_autocomplete(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for ingredients by partial name for autocomplete"""
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        # Get top matches using fuzzy search
        matches = process.extract(query_lower, self.names, scorer=fuzz.WRatio, limit=limit, score_cutoff=60)
        
        results = []
        for match_name, score, _ in matches:
            item = self.by_name[match_name]
            results.append({
                "fdc_id": item["fdc_id"],
                "name": item["name"],  # Original case
                "score": score
            })
        
        return results
