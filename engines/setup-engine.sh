#!/usr/bin/env bash
# Engine selection and automated installer
set -euo pipefail

echo "=================================================="
echo "    OpenCode APIs - Engine Setup Wizard"
echo "=================================================="

# Detect GPU presence
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    HAS_GPU=true
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
    echo "[Info] NVIDIA GPU detected: $GPU_NAME"
else
    HAS_GPU=false
    CPU_CORES=$(nproc)
    TOTAL_RAM=$(free -h | awk '/^Mem:/ {print $2}')
    echo "[Info] No NVIDIA GPU detected. Running in CPU mode ($CPU_CORES cores, $TOTAL_RAM RAM)."
fi

echo ""
echo "Select the backend inference engine to install:"
echo "1) Ollama (Recommended: Easiest, handles both CPU and GPU automatically)"
echo "2) llama.cpp (Best for ultra-budget CPU VPS without Docker)"
echo "3) vLLM (Maximum throughput for dedicated NVIDIA GPU VPS)"
read -rp "Enter choice [1-3] (Default: 1): " CHOICE
CHOICE="${CHOICE:-1}"

case "$CHOICE" in
    1)
        echo "[Setup] Installing Ollama service..."
        if ! command -v ollama &> /dev/null; then
            curl -fsSL https://ollama.com/install.sh | sh
        else
            echo "[Setup] Ollama is already installed."
        fi
        sudo systemctl enable --now ollama || true
        echo "[Setup] Ollama is running on port 11434."
        ;;
    2)
        echo "[Setup] Setting up llama.cpp server..."
        mkdir -p models
        echo "[Setup] You can run llama-server directly with ./engines/llamacpp/run-cpu.sh"
        ;;
    3)
        if [ "$HAS_GPU" = false ]; then
            echo "[Warning] vLLM requires an NVIDIA GPU with CUDA. Switching to Ollama is recommended."
        fi
        docker compose -f engines/vllm/docker-compose.yml up -d
        ;;
    *)
        echo "[Error] Invalid selection."
        exit 1
        ;;
esac

echo "[Setup] Engine configuration complete!"
