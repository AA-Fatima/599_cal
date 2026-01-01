import joblib
from pathlib import Path

MODEL_PATH = Path("models/ner_crf.joblib")

class NERModel:
    def __init__(self):
        self.crf = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

    def extract(self, text: str):
        # For demo, fallback to empty; replace with CRF/HF inference
        if not self.crf:
            return {"dishes": [], "ingredients": []}
        # Implement: tokenize, featurize, predict BIO, return spans
        return {"dishes": [], "ingredients": []}

ner_model = NERModel()