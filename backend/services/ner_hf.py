from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from settings import settings

LABELS = ["O", "B-DISH", "I-DISH", "B-ING", "I-ING"]

class HFNER:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.eval()

    def extract(self, text: str):
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
            label = LABELS[p]
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

ner_model = HFNER(settings.HF_NER_MODEL)