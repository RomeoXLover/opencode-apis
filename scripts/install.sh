#!/usr/bin/env bash
# ==============================================================================
# OpenCode APIs - Master 1-Click VPS Installer
# Installs backend engine, gateway, dependencies, and starts services.
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}        OpenCode APIs - VPS Quick Installer          ${NC}"
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
    apt-get update -y && apt-get install -y curl git ufw python3 python3-pip python3-venv nginx jq
elif command -v dnf &> /dev/null; then
    dnf install -y curl git python3 python3-pip nginx jq
fi

# 2. Install Ollama inference engine
echo -e "${BLUE}[2/5] Installing Ollama engine...${NC}"
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi
systemctl enable --now ollama

# 3. Pull recommended default coding model (Qwen 2.5 Coder 7B)
echo -e "${BLUE}[3/5] Pulling default coding model (qwen2.5-coder:7b)...${NC}"
echo -e "${YELLOW}(This may take 2-5 minutes depending on VPS network speed)${NC}"
ollama pull qwen2.5-coder:7b || echo -e "${YELLOW}Warning: Model pull failed or queued. You can pull later with ./scripts/pull-model.sh${NC}"

# 4. Setup Python Virtual Environment and Gateway
echo -e "${BLUE}[4/5] Setting up FastAPI Gateway...${NC}"
cd /root/opencode-apis/gateway 2>/dev/null || cd "$(dirname "$0")/../gateway"

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Create systemd service for Gateway
cat <<EOF > /etc/systemd/system/opencode-gateway.service
[Unit]
Description=OpenCode APIs Gateway
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment="BACKEND_URL=http://127.0.0.1:11434"
Environment="BACKEND_TYPE=ollama"
Environment="REQUIRE_API_KEY=false"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now opencode-gateway

# 5. Configure Nginx Reverse Proxy
echo -e "${BLUE}[5/5] Configuring Nginx reverse proxy...${NC}"
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
echo -e "You can now query your API using your VPS IP:"
echo -e "  Endpoint:  ${YELLOW}http://${VPS_IP}/v1/chat/completions${NC}"
echo -e "  Health:    ${YELLOW}http://${VPS_IP}/health${NC}"
echo -e "  Models:    ${YELLOW}http://${VPS_IP}/v1/models${NC}"
echo ""
echo -e "Test your API with cURL:"
echo -e "  curl http://${VPS_IP}/v1/chat/completions \\"
echo -e "    -H \"Content-Type: application/json\" \\"
echo -e "    -d '{\"model\": \"qwen2.5-coder:7b\", \"messages\": [{\"role\": \"user\", \"content\": \"Write a python hello world\"}]}'"
echo ""
echo -e "To configure a custom domain with free SSL:"
echo -e "  sudo ./nginx/ssl-setup.sh api.yourdomain.com your-email@example.com"
