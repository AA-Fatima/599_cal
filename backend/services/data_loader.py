import json
import pandas as pd

def load_usda(found_path: str, legacy_path: str):
    def read(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    data = []
    for item in read(found_path) + read(legacy_path):
        fdc_id = item.get("fdc_id") or item.get("fdcId")
        name = (item.get("description") or item.get("name") or "").strip().lower()
        calories = None
        for nutrient in item.get("foodNutrients", []):
            if str(nutrient.get("nutrientId")) in ("1008", "208"):
                calories = nutrient.get("value")
                break
        if fdc_id and name and calories is not None:
            data.append({
                "fdc_id": fdc_id,
                "name": name,
                "per_100g_calories": calories
            })
    return data

def load_dishes(xlsx_path: str):
    df = pd.read_excel(xlsx_path)
    dishes = []
    for _, row in df.iterrows():
        ingredients = []
        try:
            ingredients = json.loads(row["ingredients"])
        except Exception:
            pass
        dishes.append({
            "dish_id": int(row["dish_id"]),
            "dish_name": str(row["dish name"]).strip().lower(),
            "country": row.get("Country", ""),
            "ingredients": ingredients
        })
    return dishes