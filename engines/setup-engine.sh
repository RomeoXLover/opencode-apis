#!/usr/bin/env bash
# OpenCode Engine Setup Wizard
set -euo pipefail

echo "=================================================="
echo "    OpenCode APIs - Engine Setup Wizard"
echo "=================================================="

echo "[1/2] Installing official OpenCode package..."
if ! command -v opencode &> /dev/null && [ ! -f "/root/.opencode/bin/opencode" ]; then
    curl -fsSL https://opencode.ai/v2/install | bash -s -- --no-modify-path
    export PATH="$HOME/.opencode/bin:$PATH"
else
    echo "[Setup] OpenCode is already installed."
fi

# Ensure opencode is in PATH
export PATH="$HOME/.opencode/bin:$PATH"

echo "[2/2] Configuring OpenCode service..."
mkdir -p /root/.config/opencode
if [ -f "$(dirname "$0")/opencode/opencode.json" ]; then
    cp "$(dirname "$0")/opencode/opencode.json" /root/.config/opencode/opencode.json
fi

echo "[Setup] Starting OpenCode service on port 4096..."
cp "$(dirname "$0")/opencode/systemd/opencode.service" /etc/systemd/system/opencode.service 2>/dev/null || true
systemctl daemon-reload 2>/dev/null || true
systemctl enable --now opencode 2>/dev/null || true

echo "OpenCode engine setup completed successfully!"
