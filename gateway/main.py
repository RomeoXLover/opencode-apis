import json
import time
from typing import Any, AsyncGenerator, Dict, Optional, List
import httpx
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_PER_MINUTE])
app = FastAPI(
    title="OpenCode APIs Gateway",
    description="High-performance hybrid OpenAI-compatible API gateway supporting self-hosted open models and upstream cloud models (Claude 3.5 Sonnet, GPT-4o).",
    version="1.1.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verifies client API key against configured allowed keys if required."""
    if not settings.REQUIRE_API_KEY:
        return True
    
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"message": "Missing API key in Authorization header.", "type": "auth_error"}}
        )
    
    token = credentials.credentials.strip()
    if token not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"message": "Invalid API key provided.", "type": "auth_error"}}
        )
    return True

@app.get("/health")
async def health_check():
    """Health check endpoint to test VPS API status, local engine, and upstream routing."""
    backend_status = "unknown"
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            if settings.BACKEND_TYPE == "ollama":
                res = await client.get(f"{settings.BACKEND_URL}/api/tags")
                backend_status = "connected" if res.status_code == 200 else f"http_{res.status_code}"
            else:
                res = await client.get(f"{settings.BACKEND_URL}/health")
                backend_status = "connected" if res.status_code == 200 else f"http_{res.status_code}"
        except Exception as e:
            backend_status = f"unreachable: {str(e)}"

    return {
        "status": "healthy",
        "service": "opencode-apis-gateway",
        "backend_type": settings.BACKEND_TYPE,
        "backend_url": settings.BACKEND_URL,
        "backend_connectivity": backend_status,
        "upstream_router_enabled": settings.ENABLE_UPSTREAM_ROUTER,
        "upstream_configured": bool(settings.UPSTREAM_API_KEY),
        "timestamp": int(time.time())
    }

@app.get("/v1/models")
async def list_models(auth: bool = Depends(verify_api_key)):
    """Lists all available models: both local open models and upstream flagship models."""
    models: List[Dict[str, Any]] = []

    # 1. Fetch local VPS models from Ollama / vLLM
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            if settings.BACKEND_TYPE == "ollama":
                res = await client.get(f"{settings.BACKEND_URL}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    for m in data.get("models", []):
                        models.append({
                            "id": m.get("name"),
                            "object": "model",
                            "created": int(time.time()),
                            "owned_by": "local-vps",
                            "type": "open-weights",
                            "size_bytes": m.get("size", 0),
                            "details": m.get("details", {})
                        })
            else:
                res = await client.get(f"{settings.BACKEND_URL}/v1/models")
                if res.status_code == 200:
                    models.extend(res.json().get("data", []))
        except Exception:
            # Continue even if local backend is busy
            pass

    # 2. Add upstream flagship models (Claude 3.5 Sonnet, GPT-4o, etc.)
    if settings.ENABLE_UPSTREAM_ROUTER:
        upstream_flagships = [
            {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet (Anthropic)", "owned_by": "anthropic"},
            {"id": "claude-3-opus", "name": "Claude 3 Opus (Anthropic)", "owned_by": "anthropic"},
            {"id": "gpt-4o", "name": "GPT-4o (OpenAI)", "owned_by": "openai"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini (OpenAI)", "owned_by": "openai"},
            {"id": "o1-preview", "name": "OpenAI o1 Preview", "owned_by": "openai"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Google)", "owned_by": "google"},
            {"id": "deepseek-r1", "name": "DeepSeek R1 Reasoning", "owned_by": "deepseek"},
        ]
        for f in upstream_flagships:
            models.append({
                "id": f["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": f["owned_by"],
                "type": "upstream-cloud",
                "status": "ready" if settings.UPSTREAM_API_KEY else "requires_UPSTREAM_API_KEY"
            })

    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def chat_completions(
    request: Request,
    auth: bool = Depends(verify_api_key)
):
    """
    OpenAI-compliant chat completions endpoint.
    Routes open-weight models to local VPS and closed models (Claude 3.5 Sonnet, GPT-4o) upstream.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body payload.")

    model_req = body.get("model", settings.DEFAULT_MODEL)
    is_stream = body.get("stream", False)

    # Check if this model is an upstream flagship model (Claude, GPT-4o, Gemini)
    is_upstream = (
        model_req in settings.UPSTREAM_MODEL_ALIASES
        or model_req.startswith("anthropic/")
        or model_req.startswith("openai/")
        or model_req.startswith("google/")
    )

    client = httpx.AsyncClient(timeout=300.0)

    # CASE A: Upstream Model Routing (Claude 3.5 Sonnet, GPT-4o, etc.)
    if is_upstream:
        if not settings.UPSTREAM_API_KEY:
            await client.aclose()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "message": (
                            f"Model '{model_req}' is a proprietary cloud model. "
                            "To enable it, set 'UPSTREAM_API_KEY=your_key' (e.g. from OpenRouter.ai or Anthropic) in your .env file. "
                            "Alternatively, use a free self-hosted model like 'qwen2.5-coder:7b' or 'deepseek-coder:6.7b'."
                        ),
                        "type": "configuration_error",
                        "model": model_req
                    }
                }
            )

        # Map alias to target provider model ID
        target_model = settings.UPSTREAM_MODEL_ALIASES.get(model_req, model_req)
        forward_body = dict(body)
        forward_body["model"] = target_model

        target_url = f"{settings.UPSTREAM_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.UPSTREAM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/RomeoXLover/opencode-apis",
            "X-Title": "OpenCode APIs Gateway"
        }

        if not is_stream:
            try:
                resp = await client.post(target_url, json=forward_body, headers=headers)
                await client.aclose()
                return JSONResponse(status_code=resp.status_code, content=resp.json())
            except Exception as exc:
                await client.aclose()
                raise HTTPException(status_code=502, detail=f"Upstream provider error: {str(exc)}")

        # Streaming upstream response
        async def sse_upstream_stream() -> AsyncGenerator[bytes, None]:
            try:
                async with client.stream("POST", target_url, json=forward_body, headers=headers) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            finally:
                await client.aclose()

        return StreamingResponse(sse_upstream_stream(), media_type="text/event-stream")

    # CASE B: Local VPS Engine Routing (Qwen 2.5 Coder, DeepSeek Coder, etc.)
    target_url = f"{settings.BACKEND_URL}/v1/chat/completions"

    if not is_stream:
        try:
            resp = await client.post(target_url, json=body)
            await client.aclose()
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except httpx.RequestError as exc:
            await client.aclose()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": {"message": f"Local inference engine error: {str(exc)}", "type": "backend_error"}}
            )

    async def sse_local_stream() -> AsyncGenerator[bytes, None]:
        try:
            async with client.stream("POST", target_url, json=body) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        finally:
            await client.aclose()

    return StreamingResponse(sse_local_stream(), media_type="text/event-stream")

@app.post("/v1/completions")
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def raw_completions(
    request: Request,
    auth: bool = Depends(verify_api_key)
):
    """Raw text completion endpoint (useful for IDE code autocompletion)."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body payload.")

    target_url = f"{settings.BACKEND_URL}/v1/completions"
    client = httpx.AsyncClient(timeout=300.0)

    try:
        resp = await client.post(target_url, json=body)
        await client.aclose()
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as exc:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Inference error: {str(exc)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)
