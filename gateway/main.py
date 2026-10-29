import json
import time
from typing import Any, AsyncGenerator, Dict, Optional
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
    description="High-performance OpenAI-compatible API gateway for open-weight coding models on VPS.",
    version="1.0.0"
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
    """Health check endpoint to test VPS API status and backend connectivity."""
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
        "timestamp": int(time.time())
    }

@app.get("/v1/models")
async def list_models(auth: bool = Depends(verify_api_key)):
    """Lists all available open-source models loaded on this VPS."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if settings.BACKEND_TYPE == "ollama":
                res = await client.get(f"{settings.BACKEND_URL}/api/tags")
                if res.status_code != 200:
                    raise HTTPException(status_code=res.status_code, detail="Failed to fetch models from backend")
                data = res.json()
                models = [
                    {
                        "id": m.get("name"),
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "opencode-vps",
                        "size_bytes": m.get("size", 0),
                        "details": m.get("details", {})
                    }
                    for m in data.get("models", [])
                ]
                return {"object": "list", "data": models}
            else:
                # Forward to standard OpenAI /v1/models if vLLM or llama.cpp server
                res = await client.get(f"{settings.BACKEND_URL}/v1/models")
                return JSONResponse(status_code=res.status_code, content=res.json())
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": {"message": f"Backend inference engine unreachable: {str(exc)}", "type": "backend_error"}}
            )

@app.post("/v1/chat/completions")
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def chat_completions(
    request: Request,
    auth: bool = Depends(verify_api_key)
):
    """
    OpenAI-compliant chat completions endpoint.
    Supports both non-streaming JSON responses and streaming Server-Sent Events (SSE).
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body payload.")

    is_stream = body.get("stream", False)
    
    # Target URL based on backend
    if settings.BACKEND_TYPE == "ollama":
        target_url = f"{settings.BACKEND_URL}/v1/chat/completions"
    else:
        target_url = f"{settings.BACKEND_URL}/v1/chat/completions"

    client = httpx.AsyncClient(timeout=300.0)

    if not is_stream:
        try:
            resp = await client.post(target_url, json=body)
            await client.aclose()
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except httpx.RequestError as exc:
            await client.aclose()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": {"message": f"Failed communicating with inference backend: {str(exc)}", "type": "backend_error"}}
            )

    # Streaming generator
    async def sse_stream() -> AsyncGenerator[bytes, None]:
        try:
            async with client.stream("POST", target_url, json=body) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        finally:
            await client.aclose()

    return StreamingResponse(sse_stream(), media_type="text/event-stream")

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
