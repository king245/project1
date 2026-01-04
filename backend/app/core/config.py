import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Data Analytics Platform"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_DB: str = "langgraph_checkpoints"
    
    # In a real scenario, these would be loaded from .env
    # For now, we use defaults or mock values
    OPENAI_API_KEY: str = "mock-key"
    AWS_ACCESS_KEY_ID: str = "mock-aws-key"
    AWS_SECRET_ACCESS_KEY: str = "mock-aws-secret"
    AWS_REGION: str = "us-east-1"
    
    # Anthropic API Key
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "mock-ant-key")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
