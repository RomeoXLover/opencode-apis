import os
import shutil
from typing import List, Dict
from pydantic_settings import BaseSettings

def find_opencode_binary() -> str:
    candidates = [
        "/root/.opencode/bin/opencode",
        os.path.expanduser("~/.opencode/bin/opencode"),
        shutil.which("opencode") or "opencode"
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return "opencode"

class Settings(BaseSettings):
    # Server Host and Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Backend inference engine: OpenCode package (default)
    BACKEND_TYPE: str = os.getenv("BACKEND_TYPE", "opencode")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:4096")
    OPENCODE_BIN: str = os.getenv("OPENCODE_BIN", find_opencode_binary())
    OPENCODE_SERVER_PASSWORD: str = os.getenv("OPENCODE_SERVER_PASSWORD", "")

    # Security & Client API Keys
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")
    API_KEYS: List[str] = [
        k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()
    ]

    # Hybrid Upstream Router (For Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro)
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

    # Default fallback model for OpenCode
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "opencode/flint-40b-free")

    # Allowed CORS Origins
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
