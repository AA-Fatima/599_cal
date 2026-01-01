from datetime import datetime
from db import SessionLocal
from models import MissingDish

class MissingLog:
    def __init__(self):
        self.db = None
    
    def get_db(self):
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def log(self, user_query, payload):
        """Log a missing dish query to the database."""
        db = self.get_db()
        try:
            missing_dish = MissingDish(
                user_query=user_query,
                parsed=payload,
                suggested_ingredients=payload.get("suggested_ingredients")
            )
            db.add(missing_dish)
            db.commit()
        except Exception as e:
            print(f"Error logging missing dish: {e}")
            db.rollback()
    
    @property
    def items(self):
        """Get all logged missing dishes."""
        db = self.get_db()
        try:
            missing_dishes = db.query(MissingDish).order_by(MissingDish.created_at.desc()).limit(100).all()
            return [
                {
                    "user_query": md.user_query,
                    "payload": md.parsed,
                    "suggested_ingredients": md.suggested_ingredients,
                    "created_at": md.created_at.isoformat() if md.created_at else None
                }
                for md in missing_dishes
            ]
        except Exception as e:
            print(f"Error fetching missing dishes: {e}")
            return []

missing_log = MissingLog()