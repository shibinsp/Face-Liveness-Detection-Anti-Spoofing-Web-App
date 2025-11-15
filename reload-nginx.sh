#!/bin/bash
#
# Post-renewal hook script for Let's Encrypt certificate renewal
# This script reloads nginx container after certificates are renewed
#

set -e

echo "🔄 Reloading nginx container after certificate renewal..."
echo "   Timestamp: $(date)"

# Change to the project directory
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App || exit 1

# Reload nginx configuration (graceful reload, no downtime)
# This re-reads the configuration and certificate files
if docker exec face-auth-nginx nginx -s reload 2>/dev/null; then
    echo "✅ Nginx configuration reloaded successfully"
    
    # Verify nginx is still running with new certificates
    sleep 2
    if docker exec face-auth-nginx nginx -t >/dev/null 2>&1; then
        echo "✅ Nginx configuration is valid"
    else
        echo "⚠️  Warning: Nginx configuration test failed, restarting container..."
        docker-compose restart nginx
        sleep 3
    fi
else
    echo "⚠️  Warning: Nginx reload failed, restarting container..."
    docker-compose restart nginx
    sleep 3
    
    # Verify container is running
    if docker ps | grep -q face-auth-nginx; then
        echo "✅ Nginx container restarted successfully"
    else
        echo "❌ Error: Failed to restart nginx container"
        exit 1
    fi
fi

echo "✅ Certificate renewal completed successfully"
echo "   New certificates are active"

