# 🔐 Face Authentication & Liveness Detection System

> **Production-ready face authentication system with React frontend, FastAPI backend, and advanced anti-spoofing**

A comprehensive face authentication application featuring **user registration**, **secure login with face recognition**, **multiple face detection**, **anti-spoofing protection**, and **Docker deployment**.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![React](https://img.shields.io/badge/react-18.3%2B-61DAFB)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688)]()
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)]()
[![License](https://img.shields.io/badge/license-educational-orange)]()

---

## ✨ Key Features

### 🔐 Complete Authentication System
- **User Registration** - Capture face and store embeddings securely
- **Secure Login** - Face recognition with anti-spoofing
- **Multiple Face Detection** - Detect and recognize all faces simultaneously
- **Face Recognition** - YOLO v11 detection + DeepFace Facenet512 embeddings
- **Anti-Spoofing** - Detects printed photos, videos, and phone screens
- **User Dashboard** - Modern React interface with real-time updates
- **SQLite Database** - Persistent storage of users and face embeddings

### 🛡️ Advanced Security Features
- **Hybrid Detection System** - MediaPipe + Texture Analysis
- **Phone Screen Detection** - Identifies fake faces on phone screens
- **Texture Analysis** - 10+ anti-spoofing metrics (edges, moiré, reflection, etc.)
- **Adaptive Thresholds** - Smart detection based on face size and characteristics
- **Real-time Processing** - Instant verification with clean camera view
- **Configurable Security** - Adjustable thresholds and security levels

### 🎨 Modern Stack
- **Frontend**: React 18 + Vite + React Router
- **Backend**: FastAPI + Uvicorn
- **Face Detection**: YOLO v11
- **Face Recognition**: DeepFace (Facenet512)
- **Liveness**: MediaPipe Face Mesh
- **Anti-Spoofing**: Custom texture analysis algorithms
- **Database**: SQLite with face embeddings
- **Deployment**: Docker + Nginx

### 🐳 Docker Deployment
- **One-Command Deploy** - `docker-compose up -d`
- **Production Ready** - Nginx reverse proxy with SSL/HTTPS support
- **Cloud Compatible** - Deploy to AWS, GCP, Azure, or any server
- **Persistent Data** - Volume mounts for database and face images
- **Health Monitoring** - Automatic health checks and restart
- **Scalable Architecture** - Separate frontend and backend containers

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React App     │  Port 2524
│   (Frontend)    │  - User Interface
│   + Nginx       │  - Camera Access
└────────┬────────┘  - Real-time Updates
         │
         │ HTTP/API
         ▼
┌─────────────────┐
│   FastAPI       │  Port 8021
│   (Backend)     │  - Face Detection
│                 │  - Face Recognition
└────────┬────────┘  - Anti-Spoofing
         │
         ▼
┌─────────────────┐
│   SQLite DB     │
│   Face Storage  │
└─────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended) 🐳

```bash
# Clone the repository
git clone https://github.com/yourusername/Face-Liveness-Detection-Anti-Spoofing-Web-App.git
cd Face-Liveness-Detection-Anti-Spoofing-Web-App

# Deploy with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:2524
# Backend API: http://localhost:8021
```

**📖 Full Docker Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)
**🚀 Server Deployment:** See [SERVER_DEPLOYMENT_GUIDE.md](SERVER_DEPLOYMENT_GUIDE.md)

---

### Option 2: Local Development

#### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend server
cd backend
python api.py

# Backend will run on http://localhost:8021
```

#### Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Run development server
npm run dev

# Frontend will run on http://localhost:5173
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8021
- API Docs: http://localhost:8021/docs

---

## 📂 Project Structure

```
Face-Liveness-Detection-Anti-Spoofing-Web-App/
│
├── backend/                    # FastAPI Backend
│   ├── api.py                 # Main API server
│   ├── Dockerfile             # Backend Docker image
│   └── data/                  # User database & faces
│       ├── users.db           # SQLite database
│       └── faces/             # Stored face images
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Camera.jsx
│   │   │   ├── LiveAuthCamera.jsx
│   │   │   └── Header.jsx
│   │   ├── pages/             # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── Dockerfile             # Frontend Docker image
│   ├── nginx.conf             # Nginx configuration
│   └── package.json           # Node dependencies
│
├── core/                       # Core detection modules
│   ├── hybrid_detection.py    # Hybrid liveness detection
│   ├── anti_spoofing.py       # Anti-spoofing engine
│   ├── mediapipe_liveness.py  # MediaPipe integration
│   ├── face_recognition.py    # YOLO + DeepFace
│   └── database.py            # SQLite database manager
│
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔌 API Endpoints

### User Management
- `GET /api/users/count` - Get total registered users
- `POST /api/register` - Register new user with face
- `GET /api/user/{user_id}` - Get user information
- `DELETE /api/user/{user_id}` - Delete user account

### Authentication
- `POST /api/login` - Authenticate user with face
- `POST /api/detect-live` - Real-time face detection
- `GET /api/health` - Health check endpoint

### Features
- **Multiple Face Recognition** - Detects all faces in frame
- **Real-time Detection** - Live camera feed processing
- **Configurable Security** - Adjustable thresholds
- **Clean UI** - No bounding boxes or overlays

---

## 🛠️ Configuration

### Backend Configuration

Edit `backend/api.py`:

```python
# Initialize hybrid detector
hybrid_detector = HybridLivenessDetection(
    security_level=3,              # 1-4 (Basic to Maximum)
    variance_threshold=10,         # Texture variance
    edge_threshold=1.0,            # Edge detection
    confidence_threshold=0.20      # Anti-spoof confidence
)

# Face recognition model
face_rec = FaceRecognitionSystem(
    model_name='Facenet512'        # DeepFace model
)
```

### Frontend Configuration

Edit `frontend/src/api/config.js`:

```javascript
const API_BASE_URL = 'http://localhost:8021';
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment with SSL

```bash
# Start with production profile (includes SSL)
docker-compose --profile production up -d
```

**Requirements:**
- SSL certificates in `/etc/letsencrypt/`
- Update `nginx-proxy.conf` with your domain

---

## 📊 Technology Stack

### Frontend
- **React 18.3** - UI framework
- **Vite 5.4** - Build tool
- **React Router 6.28** - Routing
- **Axios** - HTTP client
- **React Webcam** - Camera access

### Backend
- **FastAPI 0.104** - Web framework
- **Uvicorn** - ASGI server
- **Python 3.12** - Runtime
- **SQLite** - Database

### AI/ML Models
- **YOLO v11** - Face detection
- **DeepFace** - Face recognition (Facenet512)
- **MediaPipe** - Face mesh & landmarks
- **TensorFlow 2.16** - Deep learning backend
- **OpenCV** - Image processing

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Nginx** - Web server & reverse proxy

---

## 🔒 Security Considerations

1. **Data Protection**
   - Face embeddings are stored encrypted
   - Database is persisted in Docker volumes
   - No raw images stored (only embeddings)

2. **Anti-Spoofing**
   - Multiple detection layers
   - Phone screen detection
   - Texture analysis
   - Adaptive thresholds

3. **Production Deployment**
   - Use HTTPS/SSL in production
   - Set strong CORS policies
   - Implement rate limiting
   - Use secure database passwords

---

## 📝 Development

### Run Tests

```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
flake8 backend/ core/

# JavaScript linting
cd frontend
npm run lint
```

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📄 License

This project is for educational purposes only.

---

## 🙏 Acknowledgments

- **YOLO v11** - Ultralytics
- **DeepFace** - Face recognition library
- **MediaPipe** - Google's ML solutions
- **FastAPI** - Modern Python web framework
- **React** - Facebook's UI library

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using React, FastAPI, and Computer Vision**
