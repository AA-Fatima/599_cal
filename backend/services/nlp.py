import re
from typing import Dict, Any, List
from unidecode import unidecode
from services.synonyms import apply_synonyms, canonical

quantity_re = re.compile(
    r'(?P<qty>\d+(\.\d+)?)\s*(?P<unit>g|gram|grams|kg|tbsp|tablespoon|tsp|teaspoon|piece|حبة|حبه|ملعقة كبيرة|ملعقه كبيره|م ك|ملعقة صغيرة|م ص)',
    re.IGNORECASE
)

REMOVE_WORDS = {"without", "no", "بلا", "بدون", "منزوع", "minus", "bala"}
ADD_WORDS = {"with", "add", "extra", "plus", "زيد", "اضافة", "زيادة", "ma3", "مع"}

def normalize_text(text: str) -> str:
    # basic normalization: lowercase, strip, remove diacritics-ish
    return unidecode(text).lower().strip()

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z\u0600-\u06FF]+", text)

def parse_query(text: str) -> Dict[str, Any]:
    norm = normalize_text(text)
    tokens = tokenize(norm)
    tokens = apply_synonyms(tokens)

    # detect dish candidate: take longest token or multi-token phrase (simple heuristic)
    dish = None
    if tokens:
        dish = " ".join(tokens)

    # quantities
    quantities = []
    for m in quantity_re.finditer(norm):
        qty = float(m.group("qty"))
        unit = m.group("unit").lower()
        quantities.append({"qty": qty, "unit": unit})

    # crude add/remove detection
    intent_ops = []
    for w in tokens:
        if w in REMOVE_WORDS:
            intent_ops.append("remove")
        if w in ADD_WORDS:
            intent_ops.append("add")

    return {
        "raw": text,
        "norm": norm,
        "tokens": tokens,
        "dish_guess": dish,
        "quantities": quantities,
        "ops": intent_ops,
    }