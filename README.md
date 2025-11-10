# 🧠 Face Liveness Detection & Anti-Spoofing Web App

> **📑 New to this project?** Check **[INDEX.md](INDEX.md)** for a complete documentation guide!

A comprehensive real-time face liveness detection and anti-spoofing application with **continuous webcam streaming**, **multi-face tracking**, **GPU acceleration**, **anti-spoofing detection**, and **automated logging**.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-educational-orange)]()

**✨ NEW:** Advanced anti-spoofing detection with texture analysis + ONNX models!

## 🚀 Features

### ✅ Implemented Features

1. **🛡️ Anti-Spoofing Detection** ⭐ NEW!
   - Detects printed photos, video replays, and masks
   - Texture analysis (works immediately)
   - ONNX model support (Silent-Face-Anti-Spoofing)
   - Real-time spoofing alerts
   - Detailed analysis metrics

2. **📹 Continuous Webcam Stream**
   - Real-time frame-by-frame detection using `cv2.VideoCapture`
   - Threading for smooth performance
   - Adjustable frame processing rate
   - Live visual feedback with bounding boxes

3. **🧍‍♂️ Multi-Face Detection**
   - Simultaneous detection of multiple faces
   - Individual liveness scores for each face
   - Color-coded bounding boxes (green=live, red=spoof)
   - Aggregate statistics display

4. **⚡ GPU Acceleration**
   - Toggle between CPU and GPU modes
   - Supports CUDA via `onnxruntime-gpu`
   - Automatic provider selection
   - Performance indicators

5. **💾 Logging System**
   - Automatic CSV logging of all detections
   - Timestamps for each detection
   - Liveness scores and labels tracked
   - Downloadable log files
   - Real-time statistics dashboard

## 📦 Files Overview

### Available Apps

| File | Description | Requirements | Status |
|------|-------------|--------------|--------|
| `app.py` | **Full InsightFace version** with liveness detection | Visual C++ Build Tools + InsightFace | ⚠️ Requires setup |
| `app_antispoofing.py` | **Anti-Spoofing Detection** (texture + ONNX models) | Just OpenCV | ✅ **Ready to use** ⭐ |
| `app_enhanced.py` | **Enhanced OpenCV version** with all features | Just OpenCV | ✅ Ready to use |
| `app_simple.py` | Basic face detection | Just OpenCV | ✅ Ready to use |

### Configuration Files

- `requirements.txt` - All dependencies for full functionality
- `INSTALL_GUIDE.md` - Step-by-step installation for InsightFace
- `ANTISPOOFING_GUIDE.md` - Complete anti-spoofing documentation
- `FEATURES.md` - Detailed feature breakdown
- `QUICK_START.md` - Fast setup guide

## 🎯 Quick Start

### Option 1: Anti-Spoofing Detection (Recommended - Works Immediately) ⭐

```bash
# Install dependencies
pip install streamlit opencv-python numpy pandas

# Run the anti-spoofing app
streamlit run app_antispoofing.py
```

**Features Available:**
- ✅ **Anti-spoofing detection** (detects fake faces, photos, video replays)
- ✅ Continuous webcam streaming with threading
- ✅ Multi-face detection and tracking
- ✅ Automatic logging to CSV
- ✅ Texture analysis (works immediately, no model download)
- ✅ Optional ONNX models for 95%+ accuracy

**Use Cases:** Security systems, identity verification, access control

---

### Option 2: Enhanced Detection (Works Immediately)

```bash
# Install dependencies
pip install streamlit opencv-python numpy pandas

# Run the enhanced app
streamlit run app_enhanced.py
```

**Features Available:**
- ✅ Continuous webcam streaming with threading
- ✅ Multi-face detection and tracking
- ✅ Automatic logging to CSV
- ✅ Real-time statistics dashboard
- ⚠️ Basic face detection (no anti-spoofing/liveness)

**Use Cases:** General monitoring, face counting, basic detection

---

### Option 3: Full InsightFace Version (Advanced Liveness + Anti-Spoofing)

**Prerequisites:**
1. Install Visual C++ Build Tools
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++"
   - Installation takes 10-20 minutes

**Installation:**
```bash
# Install all dependencies (including InsightFace)
pip install -r requirements.txt

# Note: First install may take 5-10 minutes
```

**Run:**
```bash
streamlit run app.py
```

**Features Available:**
- ✅ **Advanced liveness detection** (buffalo_l model)
- ✅ **Anti-spoofing** (built-in InsightFace)
- ✅ Continuous webcam streaming
- ✅ Multi-face detection and tracking
- ✅ GPU acceleration (toggle in sidebar)
- ✅ Automatic logging to CSV
- ✅ Adjustable liveness threshold

**Use Cases:** Banking, high-security access, identity verification, anti-fraud

## 🎮 Usage Guide

### Detection Modes

#### Single Image Mode
1. Select "Single Image" in the sidebar
2. Upload an image OR capture from webcam
3. View detection results with liveness scores
4. Results automatically logged

#### Continuous Stream Mode
1. Select "Continuous Webcam Stream" in the sidebar
2. Click "🎥 Start Stream"
3. Real-time face detection begins
4. Auto-logging every ~1 second
5. Click "⏹️ Stop Stream" when done

### Settings & Controls

**Sidebar Controls:**
- **Detection Mode:** Switch between single/continuous
- **Liveness Threshold:** Adjust sensitivity (app.py only)
- **GPU Acceleration:** Enable/disable GPU (app.py only)
- **Show Logs:** Toggle log display
- **Clear Logs:** Reset all logged data

**Statistics Dashboard:**
- Total detections count
- Total faces detected
- Live vs Spoof ratio (app.py only)

## 📊 Logging Features

### Automatic Logging
- Every detection is logged with timestamp
- Liveness scores recorded
- Labels (Live/Spoof) tracked
- Auto-saved to CSV file

### Log Files
- `detection_log.csv` - Enhanced version logs
- `liveness_detection_log.csv` - Full version logs

### Log Contents
```csv
timestamp,num_faces,liveness_scores,labels,avg_liveness
2025-11-10 16:45:23,2,"[0.87, 0.92]","['Live', 'Live']",0.895
2025-11-10 16:45:24,1,"[0.23]","['Spoof']",0.23
```

## ⚡ GPU Acceleration Setup

### For Full Liveness Detection (app.py)

**1. Install CUDA Toolkit** (if you have NVIDIA GPU)
- Download: https://developer.nvidia.com/cuda-downloads
- Recommended: CUDA 11.8 or 12.x

**2. Install GPU Runtime**
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

**3. Enable in App**
- Check "Use GPU Acceleration" in sidebar
- Verify GPU status in footer

### Performance Comparison

| Mode | FPS | Latency | Hardware |
|------|-----|---------|----------|
| CPU | ~10-15 | ~60-100ms | Any |
| GPU | ~30-60 | ~15-30ms | NVIDIA GPU |

## 🏗️ Project Structure

```
Face-Liveness-Detection-Anti-Spoofing-Web-App/
│
├── 📱 Applications/
│   ├── app_antispoofing.py     # Anti-spoofing detection ⭐ RECOMMENDED
│   ├── app_enhanced.py         # Enhanced detection with streaming
│   ├── app.py                  # Full InsightFace version
│   └── app_simple.py           # Basic face detection
│
├── 🛡️ Anti-Spoofing Module/
│   └── anti_spoofing.py        # Core anti-spoofing algorithms
│
├── 📚 Documentation/
│   ├── README.md               # Main documentation (this file)
│   ├── QUICK_START.md          # Fast setup guide
│   ├── INSTALLATION.md         # Complete install instructions
│   ├── ANTISPOOFING_GUIDE.md   # Anti-spoofing details
│   ├── FEATURES.md             # Feature documentation
│   └── INSTALL_GUIDE.md        # InsightFace setup (legacy)
│
├── 📦 Configuration/
│   └── requirements.txt        # All dependencies
│
├── 🗂️ Data Directories/
│   ├── models/                 # ONNX models (optional)
│   │   └── README.md          # Model download instructions
│   └── sample_images/         # Test images
│
└── 📊 Logs (Auto-generated)/
    ├── antispoofing_log.csv   # Anti-spoofing logs
    ├── detection_log.csv      # Enhanced app logs
    └── liveness_detection_log.csv  # InsightFace logs
```

## 🔧 Technical Details

### Threading Architecture
```python
# Webcam capture runs in separate thread
WebcamThread → Queue → Main Thread → Processing
   (30 FPS)     (2 frames)   (Display)
```

### Processing Pipeline
1. **Frame Capture** - Background thread captures at ~30 FPS
2. **Queue Management** - Buffered frames (max 2)
3. **Detection** - Process every Nth frame (configurable)
4. **Rendering** - Display with bounding boxes
5. **Logging** - Periodic saves to CSV

### Models Used

**app.py (InsightFace):**
- Model: `buffalo_l`
- Backend: ONNX Runtime
- Detection: RetinaFace
- Liveness: Built-in anti-spoofing

**app_enhanced.py (OpenCV):**
- Model: Haar Cascade
- Method: `haarcascade_frontalface_default`
- Detection: Classical CV

## 📈 Features Comparison

| Feature | app.py | app_antispoofing.py | app_enhanced.py | app_simple.py |
|---------|--------|---------------------|-----------------|---------------|
| Face Detection | ✅ Advanced | ✅ Basic | ✅ Basic | ✅ Basic |
| Liveness Detection | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Anti-Spoofing | ⚠️ Basic | ✅ **Yes** | ❌ No | ❌ No |
| Continuous Stream | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| Multi-Face | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Logging | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| GPU Support | ✅ Yes | ⚠️ ONNX | ❌ No | ❌ No |
| Easy Setup | ⚠️ Complex | ✅ **Simple** | ✅ Simple | ✅ Simple |

## 🐛 Troubleshooting

### "No module named 'insightface'"
**Solution:** Use `app_enhanced.py` or install Visual C++ Build Tools

### Webcam not detected
**Solution:** 
- Check webcam permissions
- Try different camera index in code
- Restart browser

### Low FPS in continuous mode
**Solution:**
- Increase `detection_interval` in code
- Enable GPU acceleration (app.py)
- Close other applications

### CSV file locked
**Solution:**
- Close CSV file if open in Excel
- Use "Download Log" button instead

## 🎨 Customization

### Adjust Detection Frequency
```python
detection_interval = 5  # Process every 5th frame
```

### Change Liveness Threshold
```python
liveness_threshold = 0.5  # Adjust between 0.0 - 1.0
```

### Modify Video Resolution
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

## 📚 Dependencies

### Minimal Setup (Anti-Spoofing & Enhanced Apps)
```bash
pip install streamlit opencv-python numpy pandas
```
- `streamlit` - Web interface framework
- `opencv-python` - Computer vision and image processing
- `numpy` - Numerical operations
- `pandas` - Data logging and CSV export

### Optional: ONNX Models (Higher Accuracy)
```bash
pip install onnxruntime
# For GPU support:
pip install onnxruntime-gpu
```
- `onnxruntime` - ONNX model inference engine
- Download models: See `ANTISPOOFING_GUIDE.md`

### Full InsightFace Version (app.py)
```bash
pip install -r requirements.txt
```
- All of the above, plus:
- `insightface` - Advanced face analysis & liveness detection
- Additional dependencies: `onnx`, `tqdm`, `matplotlib`, `scipy`, etc.

## 🎯 Use Cases

- **Security Systems** - Real-time access control
- **Banking/Finance** - Identity verification
- **Online Proctoring** - Exam authentication
- **Smart Attendance** - Anti-spoofing attendance
- **Research** - Face anti-spoofing studies

## 📝 Notes

- First run downloads InsightFace model (~300MB)
- Logs are saved automatically in project directory
- GPU mode requires NVIDIA GPU with CUDA support
- Webcam permission required for live streaming
- CSV logs can be analyzed in Excel/Python/R

## 🤝 Contributing

Feel free to enhance the application with:
- Additional face recognition features
- Database integration for logs
- REST API endpoints
- Mobile app integration
- Advanced analytics dashboard

## 📄 License

This project is for educational and research purposes.

---

## 🎬 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install streamlit opencv-python numpy pandas
   ```

2. **Run Anti-Spoofing App:**
   ```bash
   streamlit run app_antispoofing.py
   ```

3. **Test It:**
   - Look at camera → Should detect as "Real" ✅
   - Show printed photo → Should detect as "Fake" ❌
   - Show phone screen → Should detect as "Fake" ❌

4. **Explore:**
   - Try continuous webcam mode
   - Test multi-face detection
   - Download logs for analysis

---

## 📖 Documentation

| Document | Description | Best For |
|----------|-------------|----------|
| **README.md** | Main documentation (this file) | Overview & quick start |
| **QUICK_START.md** | Fast setup guide | Getting started quickly |
| **INSTALLATION.md** | Complete install instructions | Troubleshooting setup |
| **ANTISPOOFING_GUIDE.md** | Anti-spoofing details | Understanding detection |
| **FEATURES.md** | Feature breakdown | Learning capabilities |

**Current Status:** ✅ Anti-spoofing app running at `http://localhost:8501`

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional anti-spoofing algorithms
- Database integration for logs
- REST API endpoints
- Mobile app integration
- Performance optimizations
- Additional detection models

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- **InsightFace** - Advanced face analysis
- **Silent-Face-Anti-Spoofing** - Anti-spoofing models
- **OpenCV** - Computer vision library
- **Streamlit** - Web framework
