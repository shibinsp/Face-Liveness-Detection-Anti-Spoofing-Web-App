# 🔒 SSL/HTTPS Setup Instructions

This guide will help you set up SSL/HTTPS for your domains (3netra.in and www.3netra.in).

---

## 📋 Prerequisites

1. ✅ DNS records pointing to your server IP (38.242.248.213)
2. ✅ Port 80 accessible from the internet
3. ✅ Docker containers running
4. ✅ Certbot installed on the host

---

## 🚀 Quick Setup

### Step 1: Run SSL Setup Script

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App

# Option 1: Use default email (admin@3netra.in)
./setup-ssl.sh

# Option 2: Specify your email
SSL_EMAIL=your-email@example.com ./setup-ssl.sh
```

### Step 2: Enable HTTPS in Nginx

After certificates are obtained, enable HTTPS:

```bash
./enable-ssl.sh
```

---

## 📝 Detailed Steps

### Step 1: Verify DNS

```bash
# Check DNS points to your server
dig 3netra.in
dig www.3netra.in

# Both should resolve to: 38.242.248.213
```

### Step 2: Ensure Containers Are Running

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose ps

# If not running:
docker-compose up -d
```

### Step 3: Obtain SSL Certificates

```bash
# Run the SSL setup script
./setup-ssl.sh
```

The script will:
- ✅ Check DNS configuration
- ✅ Obtain Let's Encrypt certificates
- ✅ Store them in `/etc/letsencrypt/live/3netra.in/`
- ✅ Verify certificate installation

### Step 4: Enable HTTPS in Nginx

```bash
# Enable HTTPS configuration
./enable-ssl.sh
```

This will:
- ✅ Uncomment HTTPS server block in nginx.conf
- ✅ Enable HTTP to HTTPS redirect
- ✅ Restart nginx container
- ✅ Verify configuration

---

## ✅ Verification

After setup, verify HTTPS is working:

```bash
# Test HTTPS endpoint
curl -I https://3netra.in
curl -I https://www.3netra.in

# Test HTTP redirects to HTTPS
curl -I http://3netra.in
# Should see: HTTP/1.1 301 Moved Permanently

# Check certificate details
sudo certbot certificates
```

---

## 🔄 Certificate Renewal

Let's Encrypt certificates expire every 90 days. Auto-renewal is configured via systemd timer.

### Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

### Manual Renewal

```bash
sudo certbot renew

# Restart nginx after renewal
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose restart nginx
```

### Renewal Hook (Automatic)

To automatically restart nginx after renewal, create a renewal hook:

```bash
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
sudo tee /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh << 'EOF'
#!/bin/bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose restart nginx
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh
```

---

## 🐛 Troubleshooting

### Certificate Generation Fails

**Issue:** `certbot` fails with "DNS resolution failed" or "Connection refused"

**Solutions:**
1. Verify DNS points to server: `dig 3netra.in`
2. Check firewall allows port 80: `sudo ufw status`
3. Ensure nginx container is running: `docker-compose ps`
4. Check port 80 is accessible: `curl -I http://3netra.in`

### Nginx Fails to Start

**Issue:** Nginx container keeps restarting

**Solutions:**
1. Check nginx logs: `docker-compose logs nginx`
2. Test nginx config: `docker exec face-auth-nginx nginx -t`
3. Verify certificates exist: `ls -la /etc/letsencrypt/live/3netra.in/`

### HTTP Not Redirecting to HTTPS

**Issue:** HTTP still works instead of redirecting

**Solutions:**
1. Verify HTTPS block is uncommented in `nginx.conf`
2. Restart nginx: `docker-compose restart nginx`
3. Check redirect is enabled in HTTP block

---

## 📊 Configuration Files

### Nginx Configuration
- **Location:** `/root/Face-Liveness-Detection-Anti-Spoofing-Web-App/nginx.conf`
- **HTTPS Block:** Lines 108-164 (currently commented out)

### SSL Certificates
- **Location:** `/etc/letsencrypt/live/3netra.in/`
- **Files:**
  - `fullchain.pem` - Certificate chain
  - `privkey.pem` - Private key

### Scripts
- `setup-ssl.sh` - Obtain SSL certificates
- `enable-ssl.sh` - Enable HTTPS in nginx

---

## 🔐 Security Features

Once HTTPS is enabled, the following security headers are active:

- ✅ **Strict-Transport-Security** - Force HTTPS for 1 year
- ✅ **X-Frame-Options** - Prevent clickjacking
- ✅ **X-Content-Type-Options** - Prevent MIME sniffing
- ✅ **X-XSS-Protection** - XSS protection
- ✅ **Referrer-Policy** - Control referrer information

---

## 🌐 Access URLs

After SSL setup:

- ✅ **https://3netra.in** - Secure HTTPS access
- ✅ **https://www.3netra.in** - Secure HTTPS access (www)
- 🔄 **http://3netra.in** - Redirects to HTTPS
- 🔄 **http://www.3netra.in** - Redirects to HTTPS

---

## 📞 Support

For issues:
1. Check logs: `docker-compose logs nginx`
2. Verify DNS: `dig 3netra.in`
3. Test certificates: `sudo certbot certificates`
4. Review this guide

---

**Status:** Ready for SSL setup  
**Last Updated:** 2025-11-14

