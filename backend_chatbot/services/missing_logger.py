from datetime import datetime
from typing import List, Dict
from models.schemas import MissingDishLog

class MissingLogger:
    def __init__(self):
        self.logs: List[Dict] = []
    
    def log_missing_dish(self, dish_name: str, user_query: str, gpt_ingredients: List[str]):
        """Log a missing dish with details"""
        log_entry = {
            "dish_name": dish_name,
            "user_query": user_query,
            "gpt_suggested_ingredients": gpt_ingredients,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logs.append(log_entry)
    
    def get_logs(self) -> List[Dict]:
        """Get all missing dish logs"""
        return self.logs

missing_logger = MissingLogger()
