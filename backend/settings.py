from pydantic import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    REDIS_URL: str
    HF_NER_MODEL: str
    INTENT_MODEL_PATH: str
    USDA_FOUND_PATH: str
    USDA_LEGACY_PATH: str
    DISHES_XLSX_PATH: str
    LLM_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()