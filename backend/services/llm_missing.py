from settings import settings

def propose_ingredients_if_missing(text: str):
    # If using an API, implement guarded prompt here; otherwise return None
    if not settings.LLM_API_KEY:
        return None
    # Pseudo: call LLM with a system prompt to produce ingredients JSON (no calories)
    return None