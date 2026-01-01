SYNONYMS = {
    "فاهيتا": "fajita",
    "فهيتا": "fajita",
    "fahita": "fajita",
    "faheta": "fajita",
    "fjita": "fajita",
    "تبولة": "tabbouleh",
    "تبوله": "tabbouleh",
    "tabbouli": "tabbouleh",
    "tabbouleh": "tabbouleh",
    "taboule": "tabbouleh",
    "taboula": "tabbouleh",
    "بطاطا": "fries",
    "بطاطا مقلية": "fries",
    "batata": "fries",
    "fries": "fries",
    "بندورة": "tomato",
    "طماطم": "tomato",
    "tomato": "tomato",
    "زيت زيتون": "olive oil",
    "olive oil": "olive oil",
}

def canonical(term: str) -> str:
    t = term.strip().lower()
    return SYNONYMS.get(t, t)