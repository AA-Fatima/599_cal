from settings import settings

def propose_ingredients_if_missing(text: str):
    """
    Propose ingredients for a missing dish using LLM.
    
    This function uses an LLM API to suggest ingredients for dishes not in the database.
    It MUST NOT calculate or return calorie information - only ingredient names.
    
    To use this feature, set LLM_API_KEY in your environment:
    export LLM_API_KEY='your_api_key_here'  # add key here
    
    Returns:
        list or None: List of suggested ingredient names, or None if no API key
    """
    if not settings.LLM_API_KEY:
        return None
    
    # TODO: Implement LLM API call here
    # Example pseudocode:
    # import openai  # or other LLM client
    # openai.api_key = settings.LLM_API_KEY  # add key here
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a food expert. Given a dish name, "
    #          "suggest only the ingredient names. Do NOT include calories or quantities."},
    #         {"role": "user", "content": f"What are the main ingredients in {text}?"}
    #     ]
    # )
    # Parse response and return list of ingredient names
    # return parsed_ingredients
    
    return None