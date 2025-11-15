#!/bin/bash

# Enable SSL/HTTPS in nginx configuration
# Run this after obtaining SSL certificates with setup-ssl.sh
# Configuration matches 3NETRA_DOMAIN_CONFIG.md

set -e

CONFIG_FILE="/root/Face-Liveness-Detection-Anti-Spoofing-Web-App/nginx.conf"

if [ ! -f "/etc/letsencrypt/live/3netra.in/fullchain.pem" ]; then
    echo "❌ SSL certificates not found!"
    echo "Please run setup-ssl.sh first to obtain certificates."
    exit 1
fi

echo "✅ SSL certificates found. Enabling HTTPS in nginx configuration..."

# Use Python to properly uncomment the HTTPS block
python3 << 'PYTHON_SCRIPT'
import re

config_file = "/root/Face-Liveness-Detection-Anti-Spoofing-Web-App/nginx.conf"

with open(config_file, 'r') as f:
    content = f.read()

# Uncomment HTTPS server block
# Find the commented HTTPS server block and uncomment it
pattern = r'(\s+)# (server \{[^#]*listen 443 ssl;.*?\n\s+\})'
replacement = r'\1\2'

content = re.sub(
    r'(\s+)# server \{(\n\s+)#     listen 443 ssl;.*?\n\s+)# \}',
    r'\1server {\2        listen 443 ssl;',
    content,
    flags=re.DOTALL
)

# Uncomment all lines in the HTTPS block (remove leading # and spaces)
lines = content.split('\n')
in_https_block = False
uncommented_lines = []

for line in lines:
    if '# HTTPS server for domains' in line:
        in_https_block = True
        uncommented_lines.append(line)
    elif in_https_block and line.strip().startswith('# server {'):
        uncommented_lines.append(line.replace('# server {', '    server {'))
    elif in_https_block and line.strip().startswith('#     listen'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     server_name'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     # SSL'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     ssl_certificate'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     ssl_certificate_key'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     include'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     ssl_dhparam'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     # Security'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     add_header'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     # Proxy'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     location'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#         proxy'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         # Timeouts'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         proxy_connect'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         proxy_send'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         proxy_read'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         send_timeout'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         # Buffer'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         proxy_buffering'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         proxy_request'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#     # Health'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#     location /health'):
        uncommented_lines.append(line.replace('#     ', '        '))
    elif in_https_block and line.strip().startswith('#         access_log'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         return'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip().startswith('#         add_header'):
        uncommented_lines.append(line.replace('#         ', '            '))
    elif in_https_block and line.strip() == '#     }' and 'location' in ''.join(uncommented_lines[-5:]):
        uncommented_lines.append('        }')
        in_https_block = False
    elif in_https_block and line.strip() == '# }' and uncommented_lines[-1].strip() == '}':
        uncommented_lines.append('    }')
        in_https_block = False
    else:
        uncommented_lines.append(line)

content = '\n'.join(uncommented_lines)

# Write back
with open(config_file, 'w') as f:
    f.write(content)

print("✅ HTTPS server block uncommented")
PYTHON_SCRIPT

echo "✅ HTTPS enabled in nginx configuration"
echo "🔄 Restarting nginx container..."

cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose restart nginx

sleep 3

# Test nginx configuration
if docker exec face-auth-nginx nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx configuration is valid!"
    echo ""
    echo "🌐 HTTPS is now enabled:"
    echo "  - https://3netra.in"
    echo "  - https://www.3netra.in"
    echo ""
    echo "HTTP will automatically redirect to HTTPS (matches 3NETRA_DOMAIN_CONFIG.md)."
else
    echo "❌ Nginx configuration error. Please check logs:"
    docker-compose logs nginx | tail -20
    exit 1
fi
