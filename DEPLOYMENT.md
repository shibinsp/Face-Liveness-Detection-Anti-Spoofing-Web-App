# 🚀 Deployment Guide

## Docker Deployment Guide for Face Authentication System

This guide covers deploying the Face Authentication System using Docker in various environments.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git**

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB available space
- **OS**: Linux, macOS, or Windows with WSL2

### Install Docker

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin
```

**macOS:**
```bash
# Using Homebrew
brew install --cask docker
```

**Windows:**
Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App
```

### 2. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access Application

- **Frontend**: http://localhost:2524
- **Backend API**: http://localhost:8021
- **API Documentation**: http://localhost:8021/docs

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

---

## Local Development

### Development Mode

For local development with hot-reload:

#### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend
python api.py

# Access at http://localhost:8021
```

#### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Run dev server
npm run dev

# Access at http://localhost:5173
```

### Update API URL

Edit `frontend/src/api/config.js`:

```javascript
// For local development
const API_BASE_URL = 'http://localhost:8021';
```

---

## Production Deployment

### 1. Prepare Environment

#### Update Frontend API URL

Edit `frontend/src/api/config.js`:

```javascript
// For production
const API_BASE_URL = window.location.origin;  // Use same origin
// OR
const API_BASE_URL = 'https://your-domain.com';
```

#### Build Frontend

```bash
cd frontend
npm run build
```

### 2. Configure Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: face-auth-backend-prod
    restart: always
    environment:
      - PYTHONUNBUFFERED=1
      - TF_ENABLE_ONEDNN_OPTS=0
    volumes:
      - ./backend/data:/app/backend/data
      - ./logs:/app/logs
    networks:
      - face-auth-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: face-auth-frontend-prod
    ports:
      - "2524:2524"
      - "443:443"
    depends_on:
      - backend
    restart: always
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro  # SSL certificates
    networks:
      - face-auth-network

networks:
  face-auth-network:
    driver: bridge
```

### 3. Deploy to Production

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. SSL/HTTPS Setup

#### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
```

#### Update Nginx Config

Edit `frontend/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of config
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Cloud Deployment

### AWS EC2

#### 1. Launch EC2 Instance

- **Instance Type**: t3.medium or larger
- **OS**: Ubuntu 22.04 LTS
- **Security Group**: Open ports 80, 443, 8000

#### 2. Connect and Setup

```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose-plugin

# Clone repository
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App

# Deploy
docker-compose up -d
```

#### 3. Configure Domain

- Point your domain to EC2 elastic IP
- Setup SSL with Let's Encrypt
- Update frontend config

### Google Cloud Platform

#### 1. Create VM Instance

```bash
# Create instance
gcloud compute instances create face-auth-server \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB

# SSH to instance
gcloud compute ssh face-auth-server
```

#### 2. Deploy Application

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and deploy
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose up -d
```

### Azure

#### 1. Create VM

```bash
# Create resource group
az group create --name face-auth-rg --location eastus

# Create VM
az vm create \
  --resource-group face-auth-rg \
  --name face-auth-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# Open ports
az vm open-port --port 2524 --resource-group face-auth-rg --name face-auth-vm
az vm open-port --port 443 --resource-group face-auth-rg --name face-auth-vm
```

#### 2. Deploy

```bash
# SSH to VM
ssh azureuser@<vm-public-ip>

# Install Docker and deploy
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose up -d
```

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_PATH=data/users.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8021

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost,https://your-domain.com

# ML Models
MODEL_PATH=models/
YOLO_MODEL=yolo11n.pt
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
# API Configuration
VITE_API_URL=http://localhost:8021
# OR for production
VITE_API_URL=https://your-domain.com
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Health

```bash
# Backend health
curl http://localhost:8021/api/health

# Frontend health
curl http://localhost:2524/

# Service status
docker-compose ps
```

### Backup Data

```bash
# Backup database
docker cp face-auth-backend:/app/backend/data/users.db ./backup/users-$(date +%Y%m%d).db

# Backup face images
docker cp face-auth-backend:/app/backend/data/faces ./backup/faces-$(date +%Y%m%d)/
```

### Restore Data

```bash
# Restore database
docker cp ./backup/users.db face-auth-backend:/app/backend/data/users.db

# Restart services
docker-compose restart
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart with new images
docker-compose up -d

# Remove old images
docker image prune -f
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 2524
sudo lsof -i :2524

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8080:2524"  # Use port 8080 instead
```

#### 2. Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or run with sudo
sudo docker-compose up -d
```

#### 3. Container Fails to Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Rebuild container
docker-compose up -d --build backend
```

#### 4. Can't Access Camera

- Ensure HTTPS is enabled (camera requires HTTPS in production)
- Check browser permissions
- Verify SSL certificate is valid

#### 5. Face Detection Not Working

```bash
# Check backend logs
docker-compose logs backend

# Verify models are downloaded
docker exec face-auth-backend ls -la /app/

# Restart backend
docker-compose restart backend
```

### Performance Optimization

#### 1. Enable GPU Support (if available)

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

#### 2. Adjust Worker Processes

Edit `backend/Dockerfile`:

```dockerfile
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 3. Enable Caching

Add Redis for caching:

```yaml
services:
  redis:
    image: redis:alpine
    container_name: face-auth-cache
    networks:
      - face-auth-network
```

---

## Security Best Practices

1. **Use HTTPS in Production**
   - Always use SSL/TLS certificates
   - Redirect HTTP to HTTPS

2. **Secure Environment Variables**
   - Never commit `.env` files
   - Use secrets management (Docker secrets, AWS Secrets Manager)

3. **Update Regularly**
   - Keep Docker images updated
   - Update dependencies regularly
   - Apply security patches

4. **Firewall Configuration**
   - Only open necessary ports
   - Use UFW or cloud security groups
   - Implement rate limiting

5. **Database Security**
   - Regular backups
   - Encrypt sensitive data
   - Use strong passwords

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check documentation
- Review logs for errors

---

**Happy Deploying! 🚀**
