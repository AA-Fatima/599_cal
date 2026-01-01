from services.data_loader import load_usda, load_dishes
from services.unit_map import to_grams
from services.usda_lookup import UsdaLookup
from settings import settings

class DishService:
    def __init__(self):
        self.usda_lookup = UsdaLookup(settings.USDA_FOUND_PATH, settings.USDA_LEGACY_PATH)
        self.dishes = load_dishes(settings.DISHES_XLSX_PATH)
        self.dish_by_name = {d["dish_name"]: d for d in self.dishes}

    def compute(self, match):
        if match.single_ingredient and not match.found_dish:
            ing = match.single_ingredient.lower()
            qty_grams = 100.0
            if match.quantities:
                q = match.quantities[0]
                qty_grams = to_grams(ing, q["qty"], q["unit"])
            per100 = self.usda_lookup.calories_by_name(ing)
            if per100 is None:
                return {"needs_clarification": True, "message": "Ingredient not found."}
            cal = per100 * qty_grams / 100.0
            return {
                "needs_clarification": False,
                "dish": ing,
                "ingredients": [{"name": ing, "weight_g": qty_grams, "calories": round(cal,2)}],
                "total_calories": round(cal,2),
                "notes": []
            }

        dish = match.found_dish
        ingredients = []
        notes = []
        text = match.text.lower()

        for ing in dish["ingredients"]:
            name = ing.get("name", "").lower()
            weight = float(ing.get("weight_g", 0))
            if any(k in text for k in ["without", "bala", "بدون", "no"]) and name in text:
                notes.append(f"Removed {name}")
                continue
            per100 = self.usda_lookup.calories_by_name(name) if not ing.get("usda_fdc_id") else self.usda_lookup.calories_by_id(ing["usda_fdc_id"])
            cal = (per100 or 0) * weight / 100.0
            ingredients.append({"name": name, "weight_g": weight, "calories": round(cal,2)})

        for q in match.quantities:
            if "tomato" in text:
                w = to_grams("tomato", q["qty"], q["unit"])
                per100 = self.usda_lookup.calories_by_name("tomato") or 0
                ingredients.append({"name": "tomato", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g tomato")
            if "olive oil" in text or "زيت" in text:
                w = to_grams("olive oil", q["qty"], q["unit"])
                per100 = self.usda_lookup.calories_by_name("olive oil") or 0
                ingredients.append({"name": "olive oil", "weight_g": w, "calories": round(per100*w/100.0,2), "added": True})
                notes.append(f"Added {w}g olive oil")

        total = round(sum(i["calories"] for i in ingredients), 2)
        return {
            "needs_clarification": False,
            "dish": dish["dish_name"],
            "ingredients": ingredients,
            "total_calories": total,
            "notes": notes
        }