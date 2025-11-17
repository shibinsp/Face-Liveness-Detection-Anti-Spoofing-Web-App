# 🚀 Server Deployment Guide - React + FastAPI

Complete guide to deploy the Face Authentication System to your server using Docker.

---

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04/22.04 or Debian
- **RAM**: Minimum 4GB, Recommended 8GB
- **CPU**: 2+ cores
- **Storage**: 20GB available
- **Ports**: 80, 443, 8021 (open in firewall)

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Server

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Logout and login again for docker group to take effect
exit
```

### Step 2: Clone Repository

```bash
# SSH back into server
ssh user@your-server-ip

# Clone the repository
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git

# Navigate to project directory
cd Face-Liveness-Detection-Anti-Spoofing-Web-App
```

### Step 3: Copy Existing Data (Optional)

If you have existing user data from another server:

```bash
# From your local machine or old server
scp -r backend/data user@your-server-ip:/path/to/project/backend/

# This will copy:
# - backend/data/users.db (user database)
# - backend/data/faces/ (face images)
```

### Step 4: Configure Firewall

```bash
# Allow frontend, HTTPS, and backend API
sudo ufw allow 2524/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8021/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Step 5: Build and Deploy

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

Expected output:
```
NAME                    COMMAND                  SERVICE    STATUS
face-auth-backend       "uvicorn backend.api…"   backend    Up
face-auth-frontend      "/docker-entrypoint.…"   frontend   Up
```

### Step 6: Verify Deployment

```bash
# Check backend health
curl http://localhost:8021/api/health

# Expected response:
# {"status":"healthy","service":"Face Authentication API","timestamp":"..."}

# Check user count
curl http://localhost:8021/api/users/count

# Check frontend (from your browser)
# Visit: http://your-server-ip:2524
```

---

## 🌐 Access Your Application

### Local Network / Development
- **Frontend**: http://your-server-ip:2524
- **Backend API**: http://your-server-ip:2524:8021
- **API Docs**: http://your-server-ip:2524:8021/docs

### Production with Domain
- **Frontend**: https://your-domain.com:2524
- **Backend API**: https://your-domain.com:2524:8021
- **API Docs**: https://your-domain.com:2524:8021/docs

---

## 🔒 SSL/HTTPS Setup (Production)

### Option 1: Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install certbot -y

# Stop nginx/frontend temporarily
docker-compose stop frontend

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### Update Nginx Configuration

Create `frontend/nginx-ssl.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8021/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Update `docker-compose.yml` to mount SSL certificates:

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: face-auth-frontend
    ports:
      - "80:2524"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Mount SSL certificates
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - face-auth-network
```

Rebuild and restart:

```bash
# Copy SSL config
cp frontend/nginx-ssl.conf frontend/nginx.conf

# Rebuild frontend
docker-compose build frontend

# Restart all services
docker-compose down
docker-compose up -d
```

---

## 🔍 How It Works (Architecture)

### Docker Deployment Flow

```
                    Internet
                       ↓
                   Port 2524/443
                       ↓
            ┌──────────────────────┐
            │  Frontend Container  │
            │  (React + Nginx)     │
            │  Port 2524             │
            └──────────┬───────────┘
                       │
            Nginx proxies /api/* → backend:8021
                       │
                       ↓
            ┌──────────────────────┐
            │  Backend Container   │
            │  (FastAPI)           │
            │  Port 252421           │
            └──────────┬───────────┘
                       │
                       ↓
            ┌──────────────────────┐
            │  SQLite Database     │
            │  (Volume Mount)      │
            └──────────────────────┘
```

### Key Points

1. **Frontend (React)**:
   - Built as static files in Docker image
   - Served by Nginx on port 2524
   - Uses `window.location.origin` for API calls in production
   - Nginx proxies all `/api/*` requests to backend

2. **Backend (FastAPI)**:
   - Runs on port 252421 inside Docker network
   - Only accessible via Nginx proxy from outside
   - Can be accessed directly at port 252421 for debugging

3. **Database**:
   - SQLite database persisted in volume mount
   - Located at `backend/data/users.db`
   - Survives container restarts

---

## 📊 Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Check Service Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Health status
docker-compose ps --format "table {{.Name}}\t{{.Status}}"
```

### Health Checks

```bash
# Backend health
curl http://localhost:8021/api/health

# Frontend health
curl http://localhost:2524/

# User count
curl http://localhost:8021/api/users/count
```

---

## 🔄 Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose down
docker-compose up -d

# Clean old images
docker image prune -f
```

### Backup Data

```bash
# Backup database
docker cp face-auth-backend:/app/backend/data/users.db ./backup-$(date +%Y%m%d).db

# Backup face images
docker cp face-auth-backend:/app/backend/data/faces ./backup-faces-$(date +%Y%m%d)/
```

### Restore Data

```bash
# Restore database
docker cp ./backup.db face-auth-backend:/app/backend/data/users.db

# Restart backend
docker-compose restart backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

---

## 🚨 Troubleshooting

### Issue 1: Frontend Can't Connect to Backend

**Symptoms**: API calls fail with CORS or network errors

**Solution**:
```bash
# Check if backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Verify nginx proxy configuration
docker exec face-auth-frontend cat /etc/nginx/conf.d/default.conf

# Test backend directly
curl http://localhost:8021/api/health
```

### Issue 2: Port Already in Use

**Symptoms**: Error: "port is already allocated"

**Solution**:
```bash
# Find what's using the port
sudo lsof -i :2524
sudo lsof -i :8021

# Kill the process
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
ports:
  - "8080:2524"  # Use port 252480 instead
```

### Issue 3: Camera Not Working

**Symptoms**: Browser can't access camera

**Solution**:
- Camera requires HTTPS in production
- Make sure SSL is properly configured
- Check browser permissions
- Use localhost for testing (HTTP allowed)

### Issue 4: Container Fails to Start

**Symptoms**: Container exits immediately

**Solution**:
```bash
# Check logs for errors
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache

# Check if data directory exists
ls -la backend/data/

# Create if missing
mkdir -p backend/data/faces
```

### Issue 5: High Memory Usage

**Solution**:
```bash
# Reduce workers in backend/Dockerfile
# Change: --workers 1 (already set to 1)

# Restart containers
docker-compose restart

# Monitor memory
docker stats
```

---

## 📝 Environment Variables

### Backend (.env - optional)

```bash
# backend/.env
DATABASE_PATH=data/users.db
API_HOST=0.0.0.0
API_PORT=8021
CORS_ORIGINS=http://localhost,http://your-domain.com
```

### Frontend (.env - for local dev only)

```bash
# frontend/.env
VITE_API_URL=http://localhost:8021
```

**Note**: In production (Docker), frontend automatically uses `window.location.origin`

---

## ✅ Deployment Checklist

Before going live:

- [ ] Server has required resources (4GB+ RAM, 2+ CPU cores)
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured (ports 80, 443, 8021)
- [ ] Domain DNS pointing to server IP
- [ ] SSL certificates obtained (for HTTPS)
- [ ] Nginx configured for SSL (if using HTTPS)
- [ ] Backend data directory exists: `backend/data/`
- [ ] Services build successfully: `docker-compose build`
- [ ] Services start successfully: `docker-compose up -d`
- [ ] Health checks pass: `curl http://localhost:8021/api/health`
- [ ] Frontend accessible: http://your-server-ip:2524
- [ ] API docs accessible: http://your-server-ip:2524:8021/docs
- [ ] Camera works (requires HTTPS in production)
- [ ] Face registration works
- [ ] Face authentication works
- [ ] Logs show no errors: `docker-compose logs`

---

## 🎯 Quick Commands Reference

```bash
# Deploy
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose build

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Status
docker-compose ps

# Update
git pull && docker-compose build && docker-compose up -d

# Backup
docker cp face-auth-backend:/app/backend/data/users.db ./backup.db

# Clean
docker system prune -a
```

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:8021/api/health`
3. Check firewall: `sudo ufw status`
4. Review nginx config: `docker exec face-auth-frontend cat /etc/nginx/conf.d/default.conf`
5. Test backend directly: `curl http://localhost:8021/api/users/count`

---

**Your application is now deployed! 🎉**

Access it at: http://your-server-ip:2524 (or https://your-domain.com:2524 with SSL)
