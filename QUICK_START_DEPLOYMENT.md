# ⚡ Quick Start Deployment Guide

## 🚀 One-Command Deployment

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
./deploy.sh
```

Or manually:

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App
docker-compose up -d --build
```

---

## 📍 Port Configuration

| Service | Port | URL |
|---------|------|-----|
| **Backend** | 2524 | http://localhost:2524 |
| **Frontend** | 2525 | http://localhost:2525 |
| **Database** | 2523 | http://localhost:2523 |

---

## 🌐 Access URLs

The application is accessible via:

- ✅ `http://localhost:2525`
- ✅ `http://38.242.248.213:2525`
- ✅ `http://3netra.in:2525`
- ✅ `http://www.3netra.in:2525`

---

## ✅ Health Checks

```bash
# Backend
curl http://localhost:2524/_stcore/health

# Frontend
curl http://localhost:2525/health

# Database Port
curl http://localhost:2523/health
```

---

## 📋 Quick Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after changes
docker-compose up -d --build
```

---

## 📚 Full Documentation

For detailed deployment information, see:
- `DEPLOYMENT_CONFIG.md` - Complete deployment guide
- `README.md` - General project documentation
- `DOCKER_DEPLOYMENT.md` - Docker-specific guide

---

**Ready to deploy!** 🎉

