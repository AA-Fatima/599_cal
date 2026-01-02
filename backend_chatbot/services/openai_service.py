import json
from typing import Dict, Optional
from openai import OpenAI
from models.schemas import GPTResponse, Modification

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = """You are a nutrition assistant that helps parse food queries into structured data.

Your task is to:
1. Identify the food item or dish name
2. Extract any modifications (additions or removals)
3. List the main ingredients using EXACT USDA database naming conventions

CRITICAL: Use EXACT USDA names with proper formatting:
- Include descriptors like "raw", "cooked", "fresh"
- Use proper capitalization (e.g., "Grape leaves, raw")
- Include preparation method (e.g., "Rice, white, long-grain, regular, raw, enriched")
- Use full names with commas (e.g., "Oil, olive, salad or cooking" NOT "olive oil")
- Examples:
  * "Grape leaves, raw"
  * "Rice, white, long-grain, regular, raw, enriched"
  * "Onions, raw"
  * "Beef, ground, 85% lean meat / 15% fat, raw"
  * "Oil, olive, salad or cooking"
  * "Parsley, fresh"
  * "Lemon juice, raw"
  * "Tomatoes, red, ripe, raw, year round average"

Return ONLY a JSON object with this structure:
{
  "food_item": "name of the dish",
  "modifications": {
    "remove": ["ingredient to remove"],
    "add": ["ingredient to add"]
  },
  "ingredients": ["USDA formatted ingredient 1", "USDA formatted ingredient 2"]
}"""
    
    def parse_query(self, query: str) -> Optional[GPTResponse]:
        """Send user query to GPT and parse response"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Create response object
            modifications = Modification(
                remove=data.get("modifications", {}).get("remove", []),
                add=data.get("modifications", {}).get("add", [])
            )
            
            return GPTResponse(
                food_item=data.get("food_item", ""),
                modifications=modifications,
                ingredients=data.get("ingredients", [])
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
