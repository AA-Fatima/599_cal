from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from pathlib import Path
from settings import settings

LABELS = ["O", "B-DISH", "I-DISH", "B-ING", "I-ING"]

class HFNER:
    def __init__(self, model_path: str):
        self.tokenizer = None
        self.model = None
        
        # Try to load model, fallback gracefully if not available
        try:
            path = Path(model_path)
            if path.exists() or not str(path).startswith('models/'):
                # Path exists locally or is HF hub ID
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForTokenClassification.from_pretrained(model_path)
                self.model.eval()
                print(f"✓ NER HF model loaded from {model_path}")
            else:
                print(f"ℹ NER HF model not found at {model_path}, using fallback")
        except Exception as e:
            print(f"⚠ Could not load NER HF model: {e}, using fallback")

    def extract(self, text: str):
        """Extract entities from text. Falls back to empty if model not loaded."""
        if not self.model or not self.tokenizer:
            # Fallback: return empty entities
            return {"dishes": [], "ingredients": []}
        
        try:
            tokens = self.tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
            with torch.no_grad():
                logits = self.model(**{k: v for k, v in tokens.items() if k != 'offset_mapping'}).logits
            preds = logits.argmax(-1)[0].tolist()
            offsets = tokens["offset_mapping"][0].tolist()
            dishes, ings = [], []
            current = []
            current_type = None
            for (start, end), p in zip(offsets, preds):
                if start == end:
                    continue
                label = LABELS[p] if p < len(LABELS) else "O"
                if label.startswith("B-"):
                    if current and current_type:
                        (dishes if current_type=="DISH" else ings).append(" ".join(current))
                    current = [text[start:end]]
                    current_type = label.split("-")[1]
                elif label.startswith("I-") and current_type == label.split("-")[1]:
                    current.append(text[start:end])
                else:
                    if current and current_type:
                        (dishes if current_type=="DISH" else ings).append(" ".join(current))
                    current, current_type = [], None
            if current and current_type:
                (dishes if current_type=="DISH" else ings).append(" ".join(current))
            return {"dishes": dishes, "ingredients": ings}
        except Exception as e:
            print(f"⚠ NER extraction error: {e}")
            return {"dishes": [], "ingredients": []}

ner_model = HFNER(settings.HF_NER_MODEL)