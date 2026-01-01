from functools import lru_cache
from db import SessionLocal
from models import UnitConversion

# In-memory cache for unit conversions (loaded once at startup)
_unit_cache = None

def _load_unit_conversions():
    """Load all unit conversions from database into memory cache."""
    global _unit_cache
    if _unit_cache is None:
        _unit_cache = {}
        db = SessionLocal()
        try:
            conversions = db.query(UnitConversion).all()
            for conv in conversions:
                key = (conv.ingredient_group.lower(), conv.unit.lower())
                _unit_cache[key] = conv.grams
        finally:
            db.close()
    return _unit_cache

def to_grams(item: str, qty: float, unit: str) -> float:
    """Convert quantity and unit to grams for a specific item."""
    item = item.lower().strip()
    unit = unit.lower().strip()
    
    conversions = _load_unit_conversions()
    
    # Try item-specific conversion first
    key = (item, unit)
    if key in conversions:
        return qty * conversions[key]
    
    # Fall back to generic conversion
    generic_key = ("generic", unit)
    if generic_key in conversions:
        return qty * conversions[generic_key]
    
    # If no conversion found, assume grams
    return qty