import re
from services.unit_map import to_grams

quantity_re = re.compile(
    r'(?P<qty>\d+(\.\d+)?)\s*(?P<unit>g|gram|grams|kg|tbsp|tablespoon|tsp|teaspoon|piece|حبة|حبه|ملعقة كبيرة|م ك|ملعقة صغيرة|م ص)',
    re.IGNORECASE
)

def parse_quantities(text: str):
    matches = []
    for m in quantity_re.finditer(text.lower()):
        qty = float(m.group("qty"))
        unit = m.group("unit").lower()
        matches.append({"qty": qty, "unit": unit})
    return matches