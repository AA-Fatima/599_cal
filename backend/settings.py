from pydantic import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_DB: str = "calories"
    POSTGRES_USER: str = "calories"
    POSTGRES_PASSWORD: str = "supersecret"
    REDIS_URL: str = "redis://redis:6379/0"
    HF_NER_MODEL: str = "models/ner_hf"
    INTENT_MODEL_PATH: str = "models/intent.joblib"
    USDA_FOUND_PATH: str = "data/USDA_foundation.json"
    USDA_LEGACY_PATH: str = "data/USDA_sr_legacy.json"
    DISHES_XLSX_PATH: str = "data/dishes.xlsx"
    LLM_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()