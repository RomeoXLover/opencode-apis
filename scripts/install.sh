#!/usr/bin/env bash
# ==============================================================================
# OpenCode APIs - Master 1-Click VPS Installer
# Installs official OpenCode package, API gateway, dependencies, and services.
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}      OpenCode APIs - VPS Quick Installer             ${NC}"
echo -e "${BLUE}======================================================${NC}"

# Check for root / sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[Error] Please run this script with sudo or as root.${NC}"
    exit 1
fi

# Detect VPS Public IP
VPS_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || echo "YOUR_VPS_IP")
echo -e "${GREEN}[Detected VPS IP]${NC} $VPS_IP"

# 1. Update system packages
echo -e "${BLUE}[1/5] Updating system packages...${NC}"
if command -v apt-get &> /dev/null; then
    apt-get update -y && apt-get install -y curl git ufw python3 python3-pip python3-venv nginx jq nodejs npm
elif command -v dnf &> /dev/null; then
    dnf install -y curl git python3 python3-pip nginx jq nodejs npm
fi

# 2. Install official OpenCode package
echo -e "${BLUE}[2/5] Installing official OpenCode package (@opencode/cli)...${NC}"
if ! command -v opencode &> /dev/null && [ ! -f "/root/.opencode/bin/opencode" ]; then
    curl -fsSL https://opencode.ai/v2/install | bash -s -- --no-modify-path
fi
export PATH="/root/.opencode/bin:$PATH"

# Configure OpenCode defaults
mkdir -p /root/.config/opencode
cat <<'EOF' > /root/.config/opencode/opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "opencode": {
      "settings": {
        "apiKey": "public",
        "baseURL": "https://opencode.ai/inference/openai/v1"
      }
    }
  },
  "agent": {
    "build": {
      "model": "opencode/flint-40b-free"
    }
  }
}
EOF

# Setup OpenCode background systemd service
cat <<'EOF' > /etc/systemd/system/opencode.service
[Unit]
Description=OpenCode API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment="PATH=/root/.opencode/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/.opencode/bin/opencode serve --hostname 0.0.0.0 --port 4096
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now opencode

# 3. Setup Python Virtual Environment and Gateway
echo -e "${BLUE}[3/5] Setting up FastAPI Gateway...${NC}"
cd /root/opencode-apis/gateway 2>/dev/null || cd "$(dirname "$0")/../gateway"

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Create systemd service for Gateway
cat <<EOF > /etc/systemd/system/opencode-gateway.service
[Unit]
Description=OpenCode APIs Gateway
After=network.target opencode.service

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment="BACKEND_URL=http://127.0.0.1:4096"
Environment="BACKEND_TYPE=opencode"
Environment="OPENCODE_BIN=/root/.opencode/bin/opencode"
Environment="REQUIRE_API_KEY=false"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now opencode-gateway

# 4. Configure Nginx Reverse Proxy
echo -e "${BLUE}[4/5] Configuring Nginx reverse proxy...${NC}"
NGINX_CONF_SRC="$(pwd)/../nginx/opencode.conf"
if [ -f "$NGINX_CONF_SRC" ]; then
    cp "$NGINX_CONF_SRC" /etc/nginx/sites-available/opencode.conf 2>/dev/null || cp "$NGINX_CONF_SRC" /etc/nginx/conf.d/opencode.conf
    if [ -d "/etc/nginx/sites-enabled" ]; then
        ln -sf /etc/nginx/sites-available/opencode.conf /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
    fi
    nginx -t && systemctl restart nginx
fi

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}     OpenCode APIs is now LIVE on your VPS!           ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "Your API is powered by the official ${YELLOW}OpenCode package${NC}!"
echo -e "You can now query your API using your VPS IP:"
echo -e "  Endpoint:  ${YELLOW}http://${VPS_IP}/v1/chat/completions${NC}"
echo -e "  Health:    ${YELLOW}http://${VPS_IP}/health${NC}"
echo -e "  Models:    ${YELLOW}http://${VPS_IP}/v1/models${NC}"
echo ""
echo -e "Test your API with cURL:"
echo -e "  curl http://${VPS_IP}/v1/chat/completions \\"
echo -e "    -H \"Content-Type: application/json\" \\"
echo -e "    -d '{\"model\": \"opencode/flint-40b-free\", \"messages\": [{\"role\": \"user\", \"content\": \"Write a python hello world\"}]}'"
echo ""
echo -e "To configure a custom domain with free SSL:"
echo -e "  sudo ./nginx/ssl-setup.sh api.yourdomain.com your-email@example.com"
