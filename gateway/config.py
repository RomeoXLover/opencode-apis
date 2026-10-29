import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server Host and Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Backend inference engine (Ollama, llama.cpp, or vLLM)
    BACKEND_TYPE: str = os.getenv("BACKEND_TYPE", "ollama")  # "ollama", "llamacpp", "vllm"
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:11434")

    # Security & API Keys
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")
    API_KEYS: List[str] = [
        k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()
    ]

    # Rate Limiting (per minute per IP)
    RATE_LIMIT_PER_MINUTE: str = os.getenv("RATE_LIMIT_PER_MINUTE", "60/minute")

    # Default fallback model
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:7b")

    # Allowed CORS Origins
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
