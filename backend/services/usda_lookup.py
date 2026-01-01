from functools import lru_cache
from services.data_loader import load_usda
from rapidfuzz import process, fuzz

class UsdaLookup:
    def __init__(self, found, legacy):
        self.items = load_usda(found, legacy)
        self.by_name = {i["name"]: i for i in self.items}
        self.names = list(self.by_name.keys())
        self.by_id = {i["fdc_id"]: i for i in self.items}

    @lru_cache(maxsize=4096)
    def calories_by_name(self, name: str):
        name = name.lower().strip()
        if name in self.by_name:
            return self.by_name[name]["per_100g_calories"]
        m = process.extractOne(name, self.names, scorer=fuzz.WRatio, score_cutoff=70)
        if m:
            return self.by_name[m[0]]["per_100g_calories"]
        return None

    @lru_cache(maxsize=4096)
    def calories_by_id(self, fdc_id):
        it = self.by_id.get(fdc_id)
        return it["per_100g_calories"] if it else None