#!/usr/bin/env bash
# Standalone high-efficiency CPU runner using llama-server (llama.cpp)
set -euo pipefail

MODEL_PATH="${1:-models/qwen2.5-coder-7b-instruct-q4_k_m.gguf}"
THREADS="${2:-$(nproc)}"
PORT="${3:-8080}"
CTX="${4:-8192}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "[Error] Model file $MODEL_PATH not found!"
    echo "Download a GGUF model first with:"
    echo "  curl -L -o $MODEL_PATH https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
    exit 1
fi

echo "[OpenCode] Launching llama-server on CPU with $THREADS threads, context $CTX, port $PORT..."
./llama-server \
  -m "$MODEL_PATH" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --threads "$THREADS" \
  --ctx-size "$CTX" \
  --cont-batching \
  --embedding false
