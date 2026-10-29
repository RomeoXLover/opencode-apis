#!/usr/bin/env bash
# OpenCode APIs - Model Downloader and Switcher
set -euo pipefail

MODEL="${1:-}"

if [ -z "$MODEL" ]; then
    echo "=================================================="
    echo "       OpenCode APIs - Model Selector"
    echo "=================================================="
    echo "Select an open-source coding/reasoning model to pull:"
    echo ""
    echo "  [Lightweight / Budget VPS (1GB - 4GB RAM)]"
    echo "  1) qwen2.5-coder:0.5b     (Fastest, ~400MB RAM, CPU-friendly)"
    echo "  2) qwen2.5-coder:1.5b     (Fast, ~1.2GB RAM, clean code)"
    echo "  3) llama3.2:1b            (Light general reasoning, ~1GB RAM)"
    echo ""
    echo "  [Standard VPS (8GB - 16GB RAM / 6GB VRAM) - RECOMMENDED]"
    echo "  4) qwen2.5-coder:7b       (State-of-the-art coding, ~5GB RAM)"
    echo "  5) deepseek-coder:6.7b    (DeepSeek coding model, ~4.5GB RAM)"
    echo "  6) codellama:7b           (Meta's classic CodeLlama, ~5GB RAM)"
    echo "  7) starcoder2:7b          (BigCode BigCode/StarCoder2, ~5GB RAM)"
    echo ""
    echo "  [High-Performance / Dedicated GPU (16GB - 32GB+ RAM/VRAM)]"
    echo "  8) qwen2.5-coder:14b      (Elite multi-language reasoning, ~9GB RAM)"
    echo "  9) deepseek-coder-v2:16b  (MoE architecture coding model, ~10GB RAM)"
    echo " 10) qwen2.5-coder:32b      (Matches GPT-4o on coding benchmarks, ~20GB RAM)"
    echo ""
    read -rp "Enter choice [1-10] (Default 4): " SELECTION
    SELECTION="${SELECTION:-4}"

    case "$SELECTION" in
        1) MODEL="qwen2.5-coder:0.5b" ;;
        2) MODEL="qwen2.5-coder:1.5b" ;;
        3) MODEL="llama3.2:1b" ;;
        4) MODEL="qwen2.5-coder:7b" ;;
        5) MODEL="deepseek-coder:6.7b" ;;
        6) MODEL="codellama:7b" ;;
        7) MODEL="starcoder2:7b" ;;
        8) MODEL="qwen2.5-coder:14b" ;;
        9) MODEL="deepseek-coder-v2:16b" ;;
        10) MODEL="qwen2.5-coder:32b" ;;
        *) MODEL="qwen2.5-coder:7b" ;;
    esac
fi

echo "[OpenCode] Pulling model '$MODEL' from registry..."
ollama pull "$MODEL"

echo ""
echo "[Success] Model '$MODEL' is downloaded and ready!"
echo "Test it directly via your API:"
echo "curl http://localhost:8000/v1/chat/completions \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"Write a bash script to check disk space\"}]}'"
