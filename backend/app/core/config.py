from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_env: str
    database_url: str
    frontend_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
