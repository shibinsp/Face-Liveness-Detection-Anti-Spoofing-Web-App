# ⚡ Quick Reference Guide

## Common Commands

### 🐳 Docker Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild images
docker-compose build

# Remove everything (including data)
docker-compose down -v
```

### 🔧 Development

```bash
# Backend (Terminal 1)
cd backend
python api.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### 📊 Check Status

```bash
# Service status
docker-compose ps

# Backend health
curl http://localhost:8021/api/health

# User count
curl http://localhost:8021/api/users/count

# View backend logs
docker-compose logs backend --tail=50 -f

# View frontend logs
docker-compose logs frontend --tail=50 -f
```

### 💾 Database Operations

```bash
# Backup database
docker cp face-auth-backend:/app/backend/data/users.db ./backup.db

# Restore database
docker cp ./backup.db face-auth-backend:/app/backend/data/users.db
docker-compose restart backend

# View users
docker exec face-auth-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/backend/data/users.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, email FROM users')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

---

## 🌐 Access Points

### Local Development
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8021
- **API Docs**: http://localhost:8021/docs

### Docker Deployment
- **Frontend**: http://localhost:2524
- **Backend API**: http://localhost:8021
- **API Docs**: http://localhost:8021/docs

---

## 📁 Important Files

### Configuration
- `docker-compose.yml` - Docker orchestration
- `backend/api.py` - Backend API server
- `frontend/src/api/config.js` - API URL configuration
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies

### Dockerfiles
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container
- `frontend/nginx.conf` - Nginx configuration

### Data
- `backend/data/users.db` - User database
- `backend/data/faces/` - Face images

---

## 🔑 Key Features

### Frontend (React)
- User registration page
- Login with face authentication
- Dashboard after login
- Clean camera interface (no overlays)
- Real-time face detection
- Multiple face recognition

### Backend (FastAPI)
- `/api/register` - Register new user
- `/api/login` - Authenticate user
- `/api/detect-live` - Real-time face detection
- `/api/users/count` - Get user count
- `/api/health` - Health check

### Face Detection
- **YOLO v11** - Fast face detection
- **DeepFace** - Face recognition (Facenet512)
- **MediaPipe** - Face landmarks
- **Anti-Spoofing** - Fake detection

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8021
sudo lsof -i :2524

# Kill the process
sudo kill -9 <PID>
```

### Container Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Camera Not Working
- Use HTTPS in production
- Check browser permissions
- Verify camera is not in use by another app

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm backend/data/users.db
docker-compose restart backend
```

---

## 🔄 Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Clean old images
docker image prune -f
```

---

## 📦 Project Structure

```
/
├── backend/              # FastAPI backend
│   ├── api.py           # Main API
│   ├── Dockerfile       # Backend image
│   └── data/            # User data
│
├── frontend/            # React frontend
│   ├── src/             # Source code
│   ├── Dockerfile       # Frontend image
│   └── nginx.conf       # Web server config
│
├── core/                # Core modules
│   ├── hybrid_detection.py
│   ├── face_recognition.py
│   └── database.py
│
└── docker-compose.yml   # Docker config
```

---

## 📞 Need Help?

- **Documentation**: README.md, DEPLOYMENT.md
- **API Docs**: http://localhost:8021/docs
- **Logs**: `docker-compose logs -f`
- **GitHub Issues**: Create an issue

---

**Quick tips:**
- Always check logs first: `docker-compose logs -f`
- Backend must be running before frontend API calls work
- Database is persistent (survives restarts)
- Camera requires HTTPS in production
- Multiple faces can be detected simultaneously
