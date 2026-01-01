UNIT_TO_GRAMS = {
    ("generic", "g"): 1.0,
    ("generic", "gram"): 1.0,
    ("generic", "grams"): 1.0,
    ("generic", "kg"): 1000.0,
    ("generic", "tbsp"): 15.0,
    ("generic", "tsp"): 5.0,
    ("generic", "piece"): 50.0,
    ("generic", "حبة"): 50.0,
    ("generic", "حبه"): 50.0,
    ("olive oil", "tbsp"): 13.5,
    ("olive oil", "tsp"): 4.5,
    ("tomato", "piece"): 123.0,
    ("tomato", "حبة"): 123.0,
    ("apple", "large"): 223.0,
    ("apple", "medium"): 182.0,
    ("apple", "small"): 150.0,
}

def to_grams(item: str, qty: float, unit: str) -> float:
    key = (item, unit)
    generic_key = ("generic", unit)
    if key in UNIT_TO_GRAMS:
        return qty * UNIT_TO_GRAMS[key]
    if generic_key in UNIT_TO_GRAMS:
        return qty * UNIT_TO_GRAMS[generic_key]
    return qty