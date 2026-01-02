import json
import logging
from typing import Optional
from openai import OpenAI
from config import settings
from models.schemas import GPTResponse, Modifications

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key not configured. GPT parsing will be unavailable.")
        self.model = settings.OPENAI_MODEL
    
    def parse_food_query(self, user_query: str) -> Optional[GPTResponse]:
        """
        Send user query to GPT and get structured response with food items and modifications
        """
        if not self.client:
            return None
        
        system_prompt = """You are a nutrition assistant that parses user food queries.
Your task is to:
1. Identify the main food item/dish mentioned
2. Identify any modifications (items to remove or add)
3. List the ingredients using EXACT USDA naming conventions

CRITICAL: Use USDA standard names exactly as they appear in the USDA FoodData Central database:
- "Chicken, broiler, breast, meat only, raw" NOT "chicken breast"
- "Tomatoes, red, ripe, raw, year round average" NOT "tomato"
- "Bread, pita, white, enriched" NOT "pita bread"
- "Potatoes, french fried, frozen, unprepared" NOT "french fries"
- "Oil, olive, salad or cooking" NOT "olive oil"

Return a JSON object with this EXACT structure:
{
  "food_item": "name of the main dish",
  "modifications": {
    "remove": ["ingredient1", "ingredient2"],
    "add": ["ingredient3"]
  },
  "ingredients": ["USDA name 1", "USDA name 2", "USDA name 3"]
}

If the user says "without X" or "no X", put X in the remove array.
If the user says "add X" or "with extra X", put X in the add array.
List typical ingredients for the dish if it's a common dish.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Parse into our schema
            modifications = data.get("modifications", {})
            return GPTResponse(
                food_item=data.get("food_item", ""),
                modifications=Modifications(
                    remove=modifications.get("remove", []),
                    add=modifications.get("add", [])
                ),
                ingredients=data.get("ingredients", [])
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

openai_service = OpenAIService()
