from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GEMINI_API_KEY: str  # <--- If this is here, it MUST be in Render Dashboard
    
    class Config:
        env_file = ".env"
        extra = "ignore" # This prevents crashing if extra variables exist

settings = Settings()