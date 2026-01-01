from pathlib import Path
import torch
from settings import settings

LABELS = ["O", "B-DISH", "I-DISH", "B-ING", "I-ING"]

class HFNER:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
        # Try to load model, but don't fail if not available
        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification
            if Path(model_path).exists() or self._is_hf_hub_id(model_path):
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForTokenClassification.from_pretrained(model_path)
                self.model.eval()
                print(f"✓ Loaded HF NER model from {model_path}")
            else:
                print(f"Warning: NER model not found at {model_path}, using fallback")
        except Exception as e:
            print(f"Warning: Could not load NER model: {e}, using fallback")
    
    def _is_hf_hub_id(self, path: str) -> bool:
        """Check if path looks like a HuggingFace Hub ID."""
        return "/" in path and not Path(path).exists()

    def extract(self, text: str):
        """Extract dish and ingredient entities from text."""
        # If model not loaded, return empty entities
        if not self.model or not self.tokenizer:
            return {"dishes": [], "ingredients": []}
        
        try:
            tokens = self.tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
            with torch.no_grad():
                logits = self.model(**tokens).logits
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
            print(f"Error in NER extraction: {e}")
            return {"dishes": [], "ingredients": []}

ner_model = HFNER(settings.HF_NER_MODEL)