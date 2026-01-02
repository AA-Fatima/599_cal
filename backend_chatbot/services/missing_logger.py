import json
from datetime import datetime
from typing import List
from models.schemas import MissingDishLog

class MissingLoggerService:
    def __init__(self, log_file: str = "missing_dishes.json"):
        self.log_file = log_file
        self.logs: List[MissingDishLog] = []
        self._load_logs()
    
    def _load_logs(self):
        """Load existing logs from file"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.logs = [MissingDishLog(**item) for item in data]
        except FileNotFoundError:
            self.logs = []
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                data = [log.dict() for log in self.logs]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def log_missing_dish(self, dish_name: str, user_query: str, gpt_ingredients: List[str]):
        """Log a missing dish"""
        log_entry = MissingDishLog(
            dish_name=dish_name,
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            gpt_suggested_ingredients=gpt_ingredients
        )
        self.logs.append(log_entry)
        self._save_logs()
    
    def get_all_logs(self) -> List[MissingDishLog]:
        """Get all missing dish logs"""
        return self.logs
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
        self._save_logs()
