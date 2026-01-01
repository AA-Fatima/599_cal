from services.intent import intent_model
from services.ner_hf import ner_model
from services.parser import parse_quantities
from services.dish_service import DishService
from services.fuzzy_lookup import CandidateResolver
from services.llm_missing import propose_ingredients_if_missing

class Pipeline:
    def __init__(self):
        self.dish_service = DishService()
        self.cand_resolver = CandidateResolver(self.dish_service)

    def handle(self, text: str, session_id: str):
        intent, intent_conf = intent_model.predict(text)
        if intent != "calorie_query":
            return {
                "needs_clarification": True,
                "message": "I can help with calories. Please ask about a dish or ingredient."
            }

        entities = ner_model.extract(text)
        quantities = parse_quantities(text)
        match = self.cand_resolver.resolve(entities, quantities, text)

        if not match.found_dish and not match.single_ingredient:
            suggestion = propose_ingredients_if_missing(text)
            return {
                "needs_clarification": True,
                "message": "Dish not found. Please confirm or list ingredients.",
                "suggested_ingredients": suggestion
            }

        return self.dish_service.compute(match)

pipeline = Pipeline()