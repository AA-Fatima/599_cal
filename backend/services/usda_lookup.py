from functools import lru_cache
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from rapidfuzz import process, fuzz
import redis
import json
from db import SessionLocal
from models import UsdaItem
from settings import settings

# Redis cache
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None

class UsdaLookup:
    def __init__(self):
        self.db: Session = None
    
    def get_db(self):
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    @lru_cache(maxsize=4096)
    def calories_by_name(self, name: str):
        """Lookup calories by ingredient name with fuzzy matching."""
        name = name.lower().strip()
        
        # Check Redis cache first
        cache_key = f"usda:name:{name}"
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return float(cached)
            except Exception:
                pass
        
        db = self.get_db()
        
        # Try exact match first
        item = db.query(UsdaItem).filter(func.lower(UsdaItem.name) == name).first()
        if item:
            result = item.per_100g_calories
            if redis_client:
                try:
                    redis_client.setex(cache_key, 3600, str(result))
                except Exception:
                    pass
            return result
        
        # Try pg_trgm similarity search
        try:
            query = text("""
                SELECT fdc_id, name, per_100g_calories, similarity(name, :name) as sim
                FROM usda_items
                WHERE similarity(name, :name) > 0.3
                ORDER BY sim DESC
                LIMIT 1
            """)
            result = db.execute(query, {"name": name}).first()
            if result:
                calories = result[2]  # per_100g_calories
                if redis_client:
                    try:
                        redis_client.setex(cache_key, 3600, str(calories))
                    except Exception:
                        pass
                return calories
        except Exception as e:
            # Fallback to rapidfuzz if pg_trgm not available
            print(f"Warning: pg_trgm query failed, using rapidfuzz: {e}")
            pass
        
        # Fallback to rapidfuzz with in-memory search
        items = db.query(UsdaItem.name, UsdaItem.per_100g_calories).limit(10000).all()
        names = [item[0] for item in items]
        if names:
            match = process.extractOne(name, names, scorer=fuzz.WRatio, score_cutoff=70)
            if match:
                matched_name = match[0]
                item = db.query(UsdaItem).filter(UsdaItem.name == matched_name).first()
                if item:
                    result = item.per_100g_calories
                    if redis_client:
                        try:
                            redis_client.setex(cache_key, 3600, str(result))
                        except Exception:
                            pass
                    return result
        
        return None

    @lru_cache(maxsize=4096)
    def calories_by_id(self, fdc_id):
        """Lookup calories by FDC ID."""
        cache_key = f"usda:id:{fdc_id}"
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return float(cached)
            except Exception:
                pass
        
        db = self.get_db()
        item = db.query(UsdaItem).filter(UsdaItem.fdc_id == fdc_id).first()
        
        if item:
            result = item.per_100g_calories
            if redis_client:
                try:
                    redis_client.setex(cache_key, 3600, str(result))
                except Exception:
                    pass
            return result
        return None