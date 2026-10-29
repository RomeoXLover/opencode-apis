# Ollama Engine Setup for OpenCode

Ollama is the recommended default engine for general VPS deployment because it:
- Supports 1-command model downloads (`ollama run qwen2.5-coder:7b`).
- Automatically handles CPU AVX2 instructions, RAM offloading, and GPU offloading (CUDA / ROCm).
- Native OpenAI compatibility at `/v1/chat/completions`.

## Recommended Environment Flags
- `OLLAMA_KEEP_ALIVE=24h`: Keeps the model loaded in RAM/VRAM so first-token latency remains near-instant without unloading after 5 minutes.
- `OLLAMA_NUM_PARALLEL=4`: Enables handling up to 4 concurrent user requests simultaneously.
- `OLLAMA_ORIGINS=*`: Allows cross-origin requests from web frontends.
