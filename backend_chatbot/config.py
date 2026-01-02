from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    USDA_FOUND_PATH: str = "data/USDA_foundation.json"
    DISHES_XLSX_PATH: str = "data/dishes.xlsx"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_DB: str = "calories"
    POSTGRES_USER: str = "calories"
    POSTGRES_PASSWORD: str = "supersecret"
    
    class Config:
        env_file = ".env"

settings = Settings()
