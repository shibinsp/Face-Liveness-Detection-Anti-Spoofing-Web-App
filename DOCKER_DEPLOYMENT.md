# 🐳 Docker Deployment Guide

Complete guide to deploy the Face Liveness Detection & Authentication System using Docker.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Local Deployment](#local-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Variables](#environment-variables)
6. [Docker Commands](#docker-commands)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/shibinsp/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App

# Build and start
docker-compose up -d

# Access the application
# Open browser: http://localhost:8504
```

### Option 2: Docker Only

```bash
# Build the image
docker build -t face-liveness-auth .

# Run the container
docker run -d \
  --name face-auth \
  -p 8504:8504 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  face-liveness-auth

# Access the application
# Open browser: http://localhost:8504
```

---

## 📦 Prerequisites

### Required Software

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (usually included with Docker Desktop)

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU      | 2 cores | 4+ cores    |
| RAM      | 4 GB    | 8+ GB       |
| Storage  | 5 GB    | 10+ GB      |

### Check Installation

```bash
# Check Docker
docker --version
# Output: Docker version 24.0.0 or higher

# Check Docker Compose
docker-compose --version
# Output: Docker Compose version 2.0.0 or higher
```

---

## 💻 Local Deployment

### Step 1: Build the Docker Image

```bash
# Navigate to project directory
cd Face-Liveness-Detection-Anti-Spoofing-Web-App

# Build the image
docker build -t face-liveness-auth:latest .

# Verify the image
docker images | grep face-liveness-auth
```

### Step 2: Create Data Directories

```bash
# Create directories for persistent data
mkdir -p data/faces logs
```

### Step 3: Run the Container

```bash
docker run -d \
  --name face-auth \
  -p 8504:8504 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  face-liveness-auth:latest
```

### Step 4: Verify Deployment

```bash
# Check container status
docker ps

# View logs
docker logs face-auth

# Check health
docker inspect --format='{{.State.Health.Status}}' face-auth
```

### Step 5: Access the Application

Open your browser and navigate to:
- **Local**: http://localhost:8504
- **Network**: http://YOUR_SERVER_IP:8504

---

## 🌐 Production Deployment

### Using Docker Compose with Nginx

```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# Access via Nginx
# HTTP: http://your-domain.com
# HTTPS: https://your-domain.com (after SSL setup)
```

### SSL/HTTPS Setup with Let's Encrypt

1. **Install Certbot:**
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain SSL Certificate:**
```bash
# Replace with your domain
sudo certbot certonly --standalone -d your-domain.com
```

3. **Update nginx.conf:**
```bash
# Edit nginx.conf to uncomment HTTPS server block
nano nginx.conf

# Update server_name with your domain
server_name your-domain.com;

# Point to your SSL certificates
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

4. **Mount SSL certificates in docker-compose.yml:**
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/nginx/ssl:ro
```

5. **Restart services:**
```bash
docker-compose --profile production down
docker-compose --profile production up -d
```

### Production Environment Variables

Create a `.env` file:

```bash
# Application Settings
STREAMLIT_SERVER_PORT=8504
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Security (optional)
# STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
# STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200

# Database (if using external DB)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

Update docker-compose.yml to use .env:

```yaml
services:
  face-auth:
    env_file:
      - .env
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_SERVER_PORT` | 8504 | Application port |
| `STREAMLIT_SERVER_ADDRESS` | 0.0.0.0 | Bind address |
| `STREAMLIT_SERVER_HEADLESS` | true | Run without browser |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | false | Disable telemetry |
| `STREAMLIT_SERVER_FILE_WATCHER_TYPE` | none | Disable file watching |
| `STREAMLIT_SERVER_MAX_UPLOAD_SIZE` | 200 | Max upload size (MB) |

---

## 🛠️ Docker Commands

### Container Management

```bash
# Start container
docker start face-auth

# Stop container
docker stop face-auth

# Restart container
docker restart face-auth

# Remove container
docker rm -f face-auth

# View logs
docker logs -f face-auth

# Execute command in container
docker exec -it face-auth bash
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache

# Scale service (if needed)
docker-compose up -d --scale face-auth=3
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi face-liveness-auth

# Prune unused images
docker image prune -a

# Tag image for registry
docker tag face-liveness-auth:latest your-registry/face-liveness-auth:latest

# Push to registry
docker push your-registry/face-liveness-auth:latest
```

### Data Management

```bash
# Backup user data
docker exec face-auth tar czf /tmp/backup.tar.gz /app/data
docker cp face-auth:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# Restore user data
docker cp ./backup.tar.gz face-auth:/tmp/
docker exec face-auth tar xzf /tmp/backup.tar.gz -C /app/

# View database
docker exec -it face-auth sqlite3 /app/data/users.db "SELECT * FROM users;"
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs face-auth

# Check container status
docker ps -a

# Inspect container
docker inspect face-auth

# Remove and recreate
docker rm -f face-auth
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port 8504
sudo lsof -i :8504

# Kill the process
sudo kill -9 <PID>

# Or use a different port
docker run -p 8505:8504 ...
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data logs

# Or run container with specific user
docker run --user $(id -u):$(id -g) ...
```

### Out of Memory

```bash
# Check container memory usage
docker stats face-auth

# Increase container memory limit
docker run --memory="8g" ...

# Or in docker-compose.yml
services:
  face-auth:
    deploy:
      resources:
        limits:
          memory: 8G
```

### Webcam Not Working

**Note:** Docker containers have limited access to host devices like webcams. For webcam access:

```bash
# Grant device access (Linux)
docker run --device=/dev/video0 ...

# Or use host network mode
docker run --network=host ...
```

For production servers, it's recommended to:
1. Use the app on a client machine with webcam
2. Connect to the Docker server via network
3. The webcam will be accessed from the client's browser, not the server

---

## 🔒 Security Considerations

### 1. Network Security

```bash
# Use internal network for containers
networks:
  internal:
    internal: true
    
# Only expose necessary ports
ports:
  - "127.0.0.1:8504:8504"  # Only local access
```

### 2. Environment Variables

```bash
# Never commit secrets to Git
echo ".env" >> .gitignore

# Use Docker secrets for sensitive data
docker secret create db_password ./db_password.txt
```

### 3. User Permissions

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### 4. SSL/TLS

- Always use HTTPS in production
- Use strong SSL ciphers
- Keep certificates up to date

### 5. Regular Updates

```bash
# Update base image regularly
docker pull python:3.12-slim

# Rebuild with latest dependencies
docker-compose build --no-cache
```

### 6. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 Monitoring & Logging

### Container Health Monitoring

```bash
# View health status
docker inspect --format='{{.State.Health.Status}}' face-auth

# Continuous health check
watch -n 5 'docker inspect --format="{{.State.Health.Status}}" face-auth'
```

### Log Management

```bash
# View logs with timestamps
docker logs -f --timestamps face-auth

# Limit log size
docker run --log-opt max-size=10m --log-opt max-file=3 ...

# Export logs
docker logs face-auth > app.log 2>&1
```

---

## 🚢 Deployment to Cloud Platforms

### AWS ECS

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
docker tag face-liveness-auth:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/face-liveness-auth:latest
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/face-liveness-auth:latest
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/<project-id>/face-liveness-auth

# Deploy
gcloud run deploy face-auth --image gcr.io/<project-id>/face-liveness-auth --platform managed
```

### Azure Container Instances

```bash
# Create container
az container create --resource-group myResourceGroup \
  --name face-auth \
  --image face-liveness-auth:latest \
  --ports 8504 \
  --dns-name-label face-auth-unique
```

---

## 📈 Performance Optimization

### 1. Multi-stage Build (Optional)

```dockerfile
# Build stage
FROM python:3.12 AS builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage
FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
```

### 2. Docker Layer Caching

```bash
# Build with cache from registry
docker build --cache-from your-registry/face-liveness-auth:latest .
```

### 3. Resource Limits

```yaml
services:
  face-auth:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 8G
        reservations:
          cpus: '1'
          memory: 4G
```

---

## 📞 Support

- **Issues**: https://github.com/shibinsp/Face-Liveness-Detection-Anti-Spoofing-Web-App/issues
- **Docs**: See `AUTH_SYSTEM_GUIDE.md` and `QUICK_START_AUTH.md`

---

## 📄 License

This project is for educational and research purposes.

---

**Happy Deploying! 🚀**

