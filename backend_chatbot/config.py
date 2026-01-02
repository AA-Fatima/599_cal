import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USDA_FOUND_PATH: str = os.getenv("USDA_FOUND_PATH", "data/USDA_foundation.json")
    DISHES_XLSX_PATH: str = os.getenv("DISHES_XLSX_PATH", "data/dishes.xlsx")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
settings = Settings()
