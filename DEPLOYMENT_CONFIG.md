# 🚀 Deployment Configuration - Multi-Host Setup

**Last Updated:** 2025-11-14  
**Status:** Ready for Production Deployment

---

## 📋 Overview

This document describes the deployment configuration for the Face Liveness Detection application with support for multiple hosts and custom ports.

### Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| **Backend** | 2524 | Streamlit application (internal) |
| **Frontend** | 2525 | Nginx reverse proxy (public) |
| **Database** | 2523 | Reserved for future database service (SQLite currently) |

### Supported Hosts

The application accepts requests from the following hosts:
- `localhost` / `127.0.0.1`
- `38.242.248.213` (IP address)
- `3netra.in`
- `www.3netra.in`

---

## 🏗️ Architecture

```
Internet
   ↓
Nginx (Port 2525) - Frontend/Reverse Proxy
   ↓
Streamlit App (Port 2524) - Backend
   ↓
SQLite Database (./data/users.db) - File-based, no port
```

---

## 🔧 Configuration Files

### 1. docker-compose.yml

**Backend Service (face-auth):**
- Container: `face-liveness-auth`
- Port mapping: `2524:2524`
- Environment: Streamlit configured for port 2524
- Health check: `http://localhost:2524/_stcore/health`

**Frontend Service (nginx):**
- Container: `face-auth-nginx`
- Port mappings: 
  - `2525:2525` (main frontend)
  - `2523:2523` (admin/database port)

### 2. Dockerfile

- Exposes port: `2524`
- Streamlit runs on: `--server.port=2524`
- Listens on: `0.0.0.0` (all interfaces)

### 3. nginx.conf

**Main Server Block (Port 2525):**
- Listens on: `2525`
- Server names: `localhost 38.242.248.213 3netra.in www.3netra.in _`
- Proxies to: `face-auth:2524` (backend)

**Database Port (Port 2523):**
- Listens on: `2523`
- Currently redirects to main application
- Reserved for future database service

---

## 🚀 Deployment Steps

### Prerequisites

1. **Docker & Docker Compose installed**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Required ports available**
   - Port 2524 (backend)
   - Port 2525 (frontend)
   - Port 2523 (database/admin)

3. **Firewall configured**
   ```bash
   # Allow ports (if using UFW)
   sudo ufw allow 2524/tcp
   sudo ufw allow 2525/tcp
   sudo ufw allow 2523/tcp
   ```

### Step 1: Clone and Navigate

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
```

### Step 2: Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 3: Verify Deployment

```bash
# Check backend health
curl http://localhost:2524/_stcore/health

# Check frontend health
curl http://localhost:2525/health

# Check database port
curl http://localhost:2523/health
```

### Step 4: Access Application

Access the application using any of these URLs:

- **Local**: `http://localhost:2525`
- **IP Address**: `http://38.242.248.213:2525`
- **Domain**: `http://3netra.in:2525`
- **WWW Domain**: `http://www.3netra.in:2525`

**Direct Backend Access** (if needed):
- `http://localhost:2524`
- `http://38.242.248.213:2524`

---

## 🌐 DNS Configuration (Optional)

If you want to use domain names without port numbers:

### Option 1: Use Nginx on Host (Recommended)

Configure host-level Nginx to redirect:
- `3netra.in:80` → `localhost:2525`
- `www.3netra.in:80` → `localhost:2525`

### Option 2: Use Host Nginx with SSL

```nginx
# /etc/nginx/sites-available/3netra.in
server {
    listen 80;
    server_name 3netra.in www.3netra.in;
    return 301 http://$server_name:2525$request_uri;
}
```

### Option 3: Configure Firewall/Port Forwarding

If your server uses iptables or similar:
```bash
# Forward port 80 to 2525
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 2525
```

---

## 🔍 Verification & Testing

### Test Backend Directly

```bash
# Health check
curl http://localhost:2524/_stcore/health

# Should return: "ok"
```

### Test Frontend Proxy

```bash
# Health check
curl http://localhost:2525/health

# Should return: "healthy"
```

### Test All Hosts

```bash
# Test localhost
curl -H "Host: localhost" http://localhost:2525/health

# Test IP
curl -H "Host: 38.242.248.213" http://localhost:2525/health

# Test domain
curl -H "Host: 3netra.in" http://localhost:2525/health

# Test www domain
curl -H "Host: www.3netra.in" http://localhost:2525/health
```

### Browser Testing

1. Open browser
2. Navigate to: `http://3netra.in:2525` or `http://38.242.248.213:2525`
3. Verify application loads
4. Test camera access (browser will prompt for permission)
5. Test registration and login flows

---

## 📊 Service Management

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f face-auth
docker-compose logs -f nginx
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild
docker-compose build --no-cache
```

---

## 🗄️ Database Information

### Current Setup

- **Type**: SQLite (file-based)
- **Location**: `./data/users.db`
- **Volume**: `./data` mounted to `/app/data` in container
- **No separate service needed** (file-based database)

### Database Schema

```sql
-- Users table
users (id, name, email, created_at, last_login)

-- Face embeddings table
face_embeddings (id, user_id, embedding, image_path, created_at)

-- Login history table
login_history (id, user_id, login_time, liveness_score, confidence_score, status)
```

### Database Port 2523

Port 2523 is reserved for future use if migrating to:
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- Other database services

Currently, port 2523 redirects to the main application.

---

## 🔒 Security Considerations

### Firewall Rules

```bash
# Allow necessary ports
sudo ufw allow 2524/tcp comment 'Face Auth Backend'
sudo ufw allow 2525/tcp comment 'Face Auth Frontend'
sudo ufw allow 2523/tcp comment 'Face Auth Database Port'

# Deny direct backend access from internet (optional)
# Only allow through nginx proxy
```

### Security Headers

Nginx is configured with:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### SSL/HTTPS (Future)

To enable HTTPS:
1. Uncomment HTTPS server block in `nginx.conf`
2. Obtain SSL certificates (Let's Encrypt recommended)
3. Place certificates in `./ssl/` directory
4. Restart nginx service

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :2524
sudo lsof -i :2525
sudo lsof -i :2523

# Kill process if needed
sudo kill -9 <PID>
```

### Container Not Starting

```bash
# Check logs
docker-compose logs face-auth

# Check container status
docker-compose ps

# Check container resources
docker stats
```

### Nginx Not Proxying Correctly

```bash
# Check nginx configuration
docker exec face-auth-nginx nginx -t

# Reload nginx
docker exec face-auth-nginx nginx -s reload

# Check nginx logs
docker-compose logs nginx
```

### Application Not Accessible

1. **Check backend is running:**
   ```bash
   curl http://localhost:2524/_stcore/health
   ```

2. **Check frontend is running:**
   ```bash
   curl http://localhost:2525/health
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   ```

4. **Check DNS (if using domains):**
   ```bash
   nslookup 3netra.in
   dig 3netra.in
   ```

### Database Issues

```bash
# Check database file exists
ls -lh ./data/users.db

# Check database permissions
ls -la ./data/

# Fix permissions if needed
chmod 644 ./data/users.db
chmod 755 ./data/
```

---

## 📈 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:2524/_stcore/health

# Frontend health
curl http://localhost:2525/health

# Database port health
curl http://localhost:2523/health
```

### Log Monitoring

```bash
# Application logs
docker-compose logs -f face-auth

# Nginx access logs
docker-compose logs -f nginx | grep access

# Nginx error logs
docker-compose logs -f nginx | grep error
```

### Resource Monitoring

```bash
# Container resources
docker stats

# Disk usage
docker system df

# Volume usage
du -sh ./data
du -sh ./logs
```

---

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Backup Database

```bash
# Backup SQLite database
cp ./data/users.db ./data/users.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup entire data directory
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz ./data/
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# System cleanup
docker system prune -a
```

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review this document
- Check `README.md` for general information
- Check `DOCKER_DEPLOYMENT.md` for Docker-specific help

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] Docker and Docker Compose installed
- [ ] All ports (2524, 2525, 2523) are available
- [ ] Firewall rules configured
- [ ] Services start successfully (`docker-compose up -d`)
- [ ] Backend health check passes (`curl http://localhost:2524/_stcore/health`)
- [ ] Frontend health check passes (`curl http://localhost:2525/health`)
- [ ] Application accessible via all hosts (localhost, IP, domains)
- [ ] Camera permissions work in browser
- [ ] Registration and login flows work
- [ ] Database persists data correctly
- [ ] Logs are being written
- [ ] Backup strategy in place

---

**Deployment Status**: ✅ Ready  
**Last Verified**: 2025-11-14  
**Configuration Version**: 1.0.0

