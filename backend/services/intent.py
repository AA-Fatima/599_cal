import joblib
from pathlib import Path
from settings import settings

class IntentModel:
    def __init__(self, path: str):
        self.path = path
        self.vec = None
        self.clf = None
        
        # Try to load model, but don't fail if not available
        p = Path(path)
        if p.exists():
            try:
                self.vec, self.clf = joblib.load(p)
                print(f"✓ Loaded intent model from {path}")
            except Exception as e:
                print(f"Warning: Could not load intent model: {e}, using fallback")
        else:
            print(f"Warning: Intent model not found at {path}, using fallback")

    def predict(self, text: str):
        """Predict intent of the text."""
        # If model not loaded, assume calorie query (safe default)
        if not self.vec or not self.clf:
            return "calorie_query", 1.0
        
        try:
            X = self.vec.transform([text])
            proba = self.clf.predict_proba(X)[0]
            label = self.clf.classes_[proba.argmax()]
            return label, float(proba.max())
        except Exception as e:
            print(f"Error in intent prediction: {e}")
            return "calorie_query", 1.0

intent_model = IntentModel(settings.INTENT_MODEL_PATH)