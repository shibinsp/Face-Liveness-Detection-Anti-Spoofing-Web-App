#!/bin/bash

# SSL Certificate Setup Script for 3netra.in
# This script obtains Let's Encrypt SSL certificates for HTTPS

set -e

DOMAIN="3netra.in"
EMAIL="${SSL_EMAIL:-admin@3netra.in}"  # Set SSL_EMAIL environment variable or use default

echo "🔒 Setting up SSL certificates for $DOMAIN and www.$DOMAIN"
echo ""

# Check if Docker containers are running
if ! docker ps | grep -q face-auth-nginx; then
    echo "⚠️  Docker nginx container is not running. Starting containers..."
    cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
    docker-compose up -d
    echo "Waiting for containers to be ready..."
    sleep 10
fi

# Ensure certbot webroot directory exists
sudo mkdir -p /var/www/certbot
sudo chmod 755 /var/www/certbot

echo "📋 Checking DNS..."
echo "Verifying DNS points to this server..."
IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ -z "$DOMAIN_IP" ]; then
    echo "⚠️  WARNING: Cannot resolve $DOMAIN DNS. Make sure DNS is configured."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ DNS resolved: $DOMAIN -> $DOMAIN_IP"
    if [ "$DOMAIN_IP" != "$IP" ]; then
        echo "⚠️  WARNING: Domain IP ($DOMAIN_IP) doesn't match server IP ($IP)"
        echo "Certificate may fail if DNS is not properly configured."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo ""
echo "🔐 Obtaining SSL certificates..."
echo "Email for certificate notifications: $EMAIL"
echo ""

# Check if certificates already exist
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "✅ Certificates already exist for $DOMAIN"
    echo ""
    read -p "Renew/replace existing certificates? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing certificates."
        exit 0
    fi
fi

# Obtain certificates using certbot with webroot method
echo "Checking nginx configuration..."
# Temporarily comment out HTTPS block if certificates don't exist
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "⚠️  Certificates don't exist yet. Nginx will use HTTP-only mode."
    echo "After certificates are obtained, HTTPS will be enabled automatically."
fi

echo "Running certbot to obtain certificates..."
echo ""

# Ensure containers are running for certificate validation
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose up -d nginx 2>/dev/null || true
sleep 5

sudo certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --non-interactive || {
    
    echo ""
    echo "❌ Certificate generation failed!"
    echo ""
    echo "Common issues:"
    echo "1. DNS not pointing to this server"
    echo "2. Port 80 not accessible from internet"
    echo "3. Firewall blocking HTTP traffic"
    echo ""
    echo "To debug:"
    echo "  - Check DNS: dig $DOMAIN"
    echo "  - Check firewall: sudo ufw status"
    echo "  - Check if port 80 is open: sudo netstat -tlnp | grep :80"
    exit 1
}

echo ""
echo "✅ SSL certificates obtained successfully!"
echo ""

# Verify certificates
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "📜 Certificate files:"
    ls -lh /etc/letsencrypt/live/$DOMAIN/
    echo ""
    
    # Restart nginx to load new certificates
    echo "🔄 Restarting nginx container to load SSL certificates..."
    cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
    docker-compose restart nginx
    sleep 5
    
    echo ""
    echo "✅ SSL setup complete!"
    echo ""
    echo "🌐 Test HTTPS:"
    echo "  - https://$DOMAIN"
    echo "  - https://www.$DOMAIN"
    echo ""
    echo "📋 Certificate details:"
    sudo certbot certificates | grep -A 10 "$DOMAIN"
    echo ""
    echo "🔄 Auto-renewal is configured via systemd timer"
    echo "   Test renewal: sudo certbot renew --dry-run"
else
    echo "❌ Certificate files not found!"
    exit 1
fi

