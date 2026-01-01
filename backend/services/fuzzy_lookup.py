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

        dish_names = [d["dish_name"] for d in self.ds.dishes]
        if entities.get("dishes"):
            dish_query = " ".join(entities["dishes"])
            match = process.extractOne(dish_query, dish_names, scorer=fuzz.WRatio, score_cutoff=70)
            if match:
                mr.found_dish = self.ds.dish_by_name[match[0]]
                return mr

        if entities.get("ingredients"):
            ing_query = " ".join(entities["ingredients"])
            mr.single_ingredient = ing_query
            return mr

        return mr