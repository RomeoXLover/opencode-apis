import asyncio
import json
import os
import subprocess
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

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_PER_MINUTE])
app = FastAPI(
    title="OpenCode APIs Gateway",
    description="OpenAI-compatible and native REST API gateway powered by the official OpenCode package.",
    version="2.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
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
    """Health check verifying OpenCode CLI binary and backend server connectivity."""
    opencode_bin_ok = os.path.exists(settings.OPENCODE_BIN) and os.access(settings.OPENCODE_BIN, os.X_OK)
    
    server_status = "unknown"
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            res = await client.get(f"{settings.BACKEND_URL}/")
            server_status = "running" if res.status_code in (200, 401) else f"http_{res.status_code}"
        except Exception as e:
            server_status = f"offline: {str(e)}"

    return {
        "status": "healthy",
        "service": "opencode-apis-gateway",
        "engine": "opencode-package",
        "opencode_binary": settings.OPENCODE_BIN,
        "opencode_binary_available": opencode_bin_ok,
        "opencode_server_url": settings.BACKEND_URL,
        "opencode_server_status": server_status,
        "upstream_router_enabled": settings.ENABLE_UPSTREAM_ROUTER,
        "timestamp": int(time.time())
    }

@app.get("/v1/models")
async def list_models(auth: bool = Depends(verify_api_key)):
    """Lists available models supported by OpenCode and the hybrid upstream router."""
    models: List[Dict[str, Any]] = [
        # Built-in free OpenCode models
        {
            "id": "opencode/flint-40b-free",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "opencode",
            "type": "free-opencode-model",
            "description": "OpenCode native free 40B coding and reasoning model"
        },
        {
            "id": "qwen2.5-coder:7b",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "open-weights",
            "type": "coding-model",
            "description": "Alibaba Qwen 2.5 Coder 7B"
        },
        {
            "id": "deepseek-coder:6.7b",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "open-weights",
            "type": "coding-model",
            "description": "DeepSeek Coder 6.7B"
        }
    ]

    if settings.ENABLE_UPSTREAM_ROUTER:
        upstream_models = [
            {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "owned_by": "anthropic"},
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "owned_by": "anthropic"},
            {"id": "gpt-4o", "name": "GPT-4o", "owned_by": "openai"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "owned_by": "openai"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "owned_by": "google"},
            {"id": "deepseek-r1", "name": "DeepSeek R1 Reasoning", "owned_by": "deepseek"}
        ]
        for m in upstream_models:
            models.append({
                "id": m["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": m["owned_by"],
                "type": "upstream-cloud"
            })

    return {"object": "list", "data": models}

async def execute_opencode_prompt(prompt: str, model: str) -> str:
    """Executes a coding prompt using the official opencode CLI runner."""
    cmd = [settings.OPENCODE_BIN, "run", "--auto"]
    if model and model != "default":
        cmd.extend(["-m", model])
    cmd.append(prompt)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    output = stdout.decode("utf-8", errors="replace").strip()

    if not output and proc.returncode != 0:
        err_msg = stderr.decode("utf-8", errors="replace").strip()
        raise Exception(f"OpenCode execution failed: {err_msg}")

    return output or "Done."

@app.post("/v1/chat/completions")
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def chat_completions(
    request: Request,
    auth: bool = Depends(verify_api_key)
):
    """
    OpenAI-compatible chat completions endpoint powered by OpenCode package.
    Supports streaming Server-Sent Events (SSE) and JSON responses.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body payload.")

    messages = body.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="Missing 'messages' in request body.")

    model_req = body.get("model", settings.DEFAULT_MODEL)
    is_stream = body.get("stream", False)

    # Check for upstream models
    is_upstream = (
        model_req in settings.UPSTREAM_MODEL_ALIASES
        or model_req.startswith("anthropic/")
        or model_req.startswith("openai/")
        or model_req.startswith("google/")
    )

    client = httpx.AsyncClient(timeout=300.0)

    # 1. UPSTREAM ROUTER
    if is_upstream:
        if not settings.UPSTREAM_API_KEY:
            await client.aclose()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"message": f"Model '{model_req}' requires UPSTREAM_API_KEY to be set in .env."}}
            )

        target_model = settings.UPSTREAM_MODEL_ALIASES.get(model_req, model_req)
        forward_body = dict(body)
        forward_body["model"] = target_model
        target_url = f"{settings.UPSTREAM_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.UPSTREAM_API_KEY}",
            "Content-Type": "application/json"
        }

        if not is_stream:
            try:
                resp = await client.post(target_url, json=forward_body, headers=headers)
                await client.aclose()
                return JSONResponse(status_code=resp.status_code, content=resp.json())
            except Exception as exc:
                await client.aclose()
                raise HTTPException(status_code=502, detail=f"Upstream provider error: {str(exc)}")

        async def sse_upstream():
            try:
                async with client.stream("POST", target_url, json=forward_body, headers=headers) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
            finally:
                await client.aclose()

        return StreamingResponse(sse_upstream(), media_type="text/event-stream")

    # 2. OPENCODE RUNNER
    # Format messages into conversation string for OpenCode
    conversation_prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            conversation_prompt += f"[Instruction: {content}]\n"
        elif role == "user":
            conversation_prompt += f"User: {content}\n"
        elif role == "assistant":
            conversation_prompt += f"Assistant: {content}\n"
    conversation_prompt += "Assistant: "

    req_id = f"chatcmpl-opencode-{int(time.time()*1000)}"

    if not is_stream:
        try:
            result_text = await execute_opencode_prompt(conversation_prompt, model_req)
            return {
                "id": req_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_req,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(conversation_prompt.split()),
                    "completion_tokens": len(result_text.split()),
                    "total_tokens": len(conversation_prompt.split()) + len(result_text.split())
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Streaming mode
    async def sse_opencode_stream() -> AsyncGenerator[bytes, None]:
        try:
            result_text = await execute_opencode_prompt(conversation_prompt, model_req)
            # Yield token chunks
            words = result_text.split(" ")
            for i, word in enumerate(words):
                chunk_content = word + (" " if i < len(words) - 1 else "")
                chunk_data = {
                    "id": req_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model_req,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": chunk_content},
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n".encode("utf-8")
                await asyncio.sleep(0.02)

            # Stop chunk
            final_data = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_req,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(final_data)}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        except Exception as err:
            err_payload = {"error": {"message": str(err)}}
            yield f"data: {json.dumps(err_payload)}\n\n".encode("utf-8")

    return StreamingResponse(sse_opencode_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)
