#!/usr/bin/env bash
# Automated SSL certificate generation with Certbot for custom domains
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: sudo $0 <your-domain.com> <your-email@example.com>"
    echo "Example: sudo $0 api.mydomain.com admin@mydomain.com"
    exit 1
fi

DOMAIN="$1"
EMAIL="$2"

echo "[SSL] Installing Certbot and Nginx plugin..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y certbot python3-certbot-nginx
elif command -v dnf &> /dev/null; then
    sudo dnf install -y certbot python3-certbot-nginx
fi

echo "[SSL] Obtaining free Let's Encrypt TLS/SSL certificate for $DOMAIN..."
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect

echo "[SSL] Testing automatic certificate renewal..."
sudo certbot renew --dry-run

echo "[SSL] SSL is now live on https://$DOMAIN"
