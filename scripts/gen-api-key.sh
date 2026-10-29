#!/usr/bin/env bash
# OpenCode APIs - API Key Generator
set -euo pipefail

ENV_FILE="$(dirname "$0")/../gateway/.env"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$(dirname "$0")/../.env"
fi

# Generate cryptographically secure random token (32 hex characters with 'sk-opencode-' prefix)
RAND_TOKEN=$(python3 -c "import secrets; print('sk-opencode-' + secrets.token_hex(16))")

echo "Generated API Key: $RAND_TOKEN"

if [ -f "$ENV_FILE" ]; then
    if grep -q "API_KEYS=" "$ENV_FILE"; then
        sed -i "s/API_KEYS=\(.*\)/API_KEYS=\1,$RAND_TOKEN/" "$ENV_FILE"
        sed -i "s/API_KEYS=,/API_KEYS=/" "$ENV_FILE"
    else
        echo "API_KEYS=$RAND_TOKEN" >> "$ENV_FILE"
    fi
    echo "[Saved] Added key to $ENV_FILE"
    echo "Remember to restart opencode-gateway if it is already running:"
    echo "  sudo systemctl restart opencode-gateway"
else
    echo "Create a .env file with: API_KEYS=$RAND_TOKEN"
fi
