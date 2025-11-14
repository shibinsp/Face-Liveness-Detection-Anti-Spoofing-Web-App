# Project Structure

```
Face-Liveness-Detection-Anti-Spoofing-Web-App/
│
├── apps/                          # Application entry points
│   ├── __init__.py
│   ├── app_auth.py                # Face authentication system ⭐⭐⭐ COMPLETE SOLUTION
│   ├── app_hybrid.py              # Hybrid detection (MediaPipe + Anti-spoofing) ⭐ RECOMMENDED
│   ├── app.py                     # Full InsightFace version (requires Visual C++ Build Tools)
│   ├── app_antispoofing.py        # Anti-spoofing detection only
│   ├── app_enhanced.py            # Enhanced OpenCV version
│   └── app_simple.py              # Basic face detection
│
├── core/                          # Core modules
│   ├── __init__.py
│   ├── anti_spoofing.py           # Anti-spoofing detection algorithms
│   ├── hybrid_detection.py        # Hybrid detection logic
│   ├── mediapipe_liveness.py      # MediaPipe liveness detection
│   ├── database.py                # User database management
│   └── face_recognition.py        # Face recognition with YOLO v11
│
├── docs/                          # Documentation
│   ├── README_HYBRID.md
│   ├── HYBRID_DETECTION_GUIDE.md
│   ├── ANTISPOOFING_GUIDE.md
│   ├── INSTALLATION.md
│   ├── QUICK_START.md
│   └── ... (other documentation files)
│
├── models/                        # Model files (ONNX models go here)
│   └── README.md
│
├── data/                          # User data (auto-generated)
│   ├── users.db                   # SQLite database
│   └── faces/                     # User face images
│
├── sample_images/                 # Sample test images
│   ├── image.png
│   └── image1.png
│
├── requirements.txt               # Python dependencies
├── README.md                      # Main project documentation
├── AUTH_SYSTEM_GUIDE.md           # Authentication system documentation
├── .gitignore                     # Git ignore rules
└── PROJECT_STRUCTURE.md           # This file
```

## Quick Start

### Run Authentication System (Complete Solution)
```bash
streamlit run apps/app_auth.py
```

**Features:**
- User registration with face capture
- Secure login with face recognition + liveness detection
- Two-factor authentication
- User dashboard

### Run Hybrid Detection (Recommended)
```bash
streamlit run apps/app_hybrid.py
```

### Run Anti-Spoofing Only
```bash
streamlit run apps/app_antispoofing.py
```

### Run Full InsightFace Version
```bash
streamlit run apps/app.py
```

## Module Organization

- **apps/**: Streamlit application files (UI layer)
- **core/**: Core detection algorithms (business logic)
- **docs/**: Documentation and guides
- **models/**: Pre-trained model files (download separately)
- **sample_images/**: Test images

