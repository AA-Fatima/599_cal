import joblib
from pathlib import Path
from settings import settings

class IntentModel:
    def __init__(self, path: str):
        p = Path(path)
        if p.exists():
            self.vec, self.clf = joblib.load(p)
        else:
            self.vec, self.clf = None, None

    def predict(self, text: str):
        if not self.vec:
            return "calorie_query", 1.0
        X = self.vec.transform([text])
        proba = self.clf.predict_proba(X)[0]
        label = self.clf.classes_[proba.argmax()]
        return label, float(proba.max())

intent_model = IntentModel(settings.INTENT_MODEL_PATH)