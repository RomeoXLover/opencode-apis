import os
from typing import List, Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server Host and Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Backend inference engine for self-hosted local models (Ollama, llama.cpp, or vLLM)
    BACKEND_TYPE: str = os.getenv("BACKEND_TYPE", "ollama")  # "ollama", "llamacpp", "vllm"
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:11434")

    # Security & API Keys
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")
    API_KEYS: List[str] = [
        k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()
    ]

    # Hybrid Upstream Router (For Closed Models like Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro)
    ENABLE_UPSTREAM_ROUTER: bool = os.getenv("ENABLE_UPSTREAM_ROUTER", "true").lower() in ("true", "1", "yes")
    UPSTREAM_API_KEY: str = os.getenv("UPSTREAM_API_KEY", "")
    UPSTREAM_BASE_URL: str = os.getenv("UPSTREAM_BASE_URL", "https://openrouter.ai/api/v1")

    # Model alias routing map for closed-source models
    UPSTREAM_MODEL_ALIASES: Dict[str, str] = {
        "claude-3-5-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-3-5-sonnet-20241022": "anthropic/claude-3.5-sonnet",
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3-haiku": "anthropic/claude-3-haiku",
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "o1-preview": "openai/o1-preview",
        "o1-mini": "openai/o1-mini",
        "gemini-1.5-pro": "google/gemini-pro-1.5",
        "gemini-1.5-flash": "google/gemini-flash-1.5",
        "deepseek-r1": "deepseek/deepseek-r1",
        "deepseek-v3": "deepseek/deepseek-chat"
    }

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
