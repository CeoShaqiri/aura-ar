#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# init-letsencrypt.sh  —  Run ONCE on the Hetzner server to bootstrap SSL.
#
# The chicken-and-egg problem:
#   Nginx needs the cert to start HTTPS, but Certbot needs Nginx running
#   on port 80 to get the cert.
#
# Solution:
#   1. Start Nginx with HTTP-only (ports 80 only, no SSL block yet).
#   2. Certbot obtains the cert via the HTTP webroot challenge.
#   3. Nginx restarts with the full nginx.conf (HTTP + HTTPS).
#
# Usage (run as root on your Hetzner server):
#   chmod +x init-letsencrypt.sh
#   ./init-letsencrypt.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

DOMAIN="ceo.aura-intelligence.ch"
EMAIL="admin@aura-intelligence.ch"   # ← Change to your real email for renewal alerts

echo "=== Step 1: Start Nginx in HTTP-only mode ==="
# Temporarily replace nginx.conf with a minimal HTTP-only config
cp nginx.conf nginx.conf.bak
cat > /tmp/nginx-init.conf <<'EOF'
server {
    listen 80;
    server_name ceo.aura-intelligence.ch;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 200 'Initializing SSL...';
        add_header Content-Type text/plain;
    }
}
EOF
cp /tmp/nginx-init.conf nginx.conf
docker compose up -d nginx

echo "=== Step 2: Obtain certificate from Let's Encrypt ==="
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

echo "=== Step 3: Restore full Nginx config (HTTP + HTTPS) ==="
cp nginx.conf.bak nginx.conf
docker compose up -d nginx

echo ""
echo "✅ SSL certificate obtained for $DOMAIN"
echo "✅ Your server is now live at https://$DOMAIN"
echo ""
echo "The Certbot container will auto-renew every 12 hours."
