from datetime import datetime

class MissingLog:
    def __init__(self):
        self.items = []

    def log(self, user_query, payload):
        self.items.append({
            "user_query": user_query,
            "payload": payload,
            "created_at": datetime.utcnow().isoformat()
        })

missing_log = MissingLog()