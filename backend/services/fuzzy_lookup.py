from rapidfuzz import process, fuzz

class MatchResult:
    def __init__(self):
        self.found_dish = None
        self.single_ingredient = None
        self.entities = None
        self.quantities = None
        self.text = None

class CandidateResolver:
    def __init__(self, dish_service):
        self.ds = dish_service

    def resolve(self, entities, quantities, text):
        mr = MatchResult()
        mr.entities = entities
        mr.quantities = quantities
        mr.text = text

        # Try to find dish from NER entities
        if entities.get("dishes"):
            dish_query = " ".join(entities["dishes"])
            dish = self.ds.get_dish_by_name(dish_query)
            if dish:
                mr.found_dish = dish
                return mr

        # If no dish, check for single ingredient
        if entities.get("ingredients"):
            ing_query = " ".join(entities["ingredients"])
            mr.single_ingredient = ing_query
            return mr

        return mr