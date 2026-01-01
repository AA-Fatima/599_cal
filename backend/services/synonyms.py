from functools import lru_cache
from db import SessionLocal
from models import Synonym

# In-memory cache for synonyms (loaded once at startup)
_synonym_cache = None

def _load_synonyms():
    """Load all synonyms from database into memory cache."""
    global _synonym_cache
    if _synonym_cache is None:
        _synonym_cache = {}
        db = SessionLocal()
        try:
            synonyms = db.query(Synonym).all()
            for syn in synonyms:
                _synonym_cache[syn.term.lower()] = syn.canonical.lower()
        finally:
            db.close()
    return _synonym_cache

def canonical(term: str) -> str:
    """Get canonical form of a term, or return original if not found."""
    t = term.strip().lower()
    synonyms = _load_synonyms()
    return synonyms.get(t, t)

def apply_synonyms(tokens: list) -> list:
    """Apply synonym mapping to a list of tokens."""
    return [canonical(t) for t in tokens]