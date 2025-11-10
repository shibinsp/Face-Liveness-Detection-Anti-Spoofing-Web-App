# 🚀 Quick Start Guide

## Choose Your App

### 1. 🛡️ Anti-Spoofing Detection (RECOMMENDED) ⭐

**Best for:** Security applications, detecting fake faces

**What it does:**
- Detects real faces vs printed photos
- Identifies video replays on screens
- Detects mask attacks
- Real-time webcam monitoring

**Run it:**
```bash
streamlit run app_antispoofing.py
```

**Works immediately!** No model download required (texture analysis)

---

### 2. 📹 Enhanced Detection

**Best for:** General face detection, tracking multiple faces

**What it does:**
- Continuous webcam streaming
- Multi-face detection
- Logging and statistics
- Real-time monitoring

**Run it:**
```bash
streamlit run app_enhanced.py
```

---

### 3. 🧠 Full Liveness Detection

**Best for:** Advanced liveness verification, highest accuracy

**What it does:**
- Advanced liveness detection (InsightFace)
- GPU acceleration
- Anti-spoofing
- All features combined

**Requirements:** Visual C++ Build Tools + InsightFace

**Run it:**
```bash
# After setup (see INSTALL_GUIDE.md)
streamlit run app.py
```

---

## Installation

### Quick Setup (Apps 1 & 2) - 2 minutes

```bash
# Install core dependencies
pip install streamlit opencv-python numpy pandas

# Optional: For ONNX models (higher accuracy)
pip install onnxruntime
```

### Full Setup (App 3) - 15-30 minutes

Requires Visual C++ Build Tools. See `INSTALL_GUIDE.md` for complete instructions.

```bash
pip install -r requirements.txt
```

---

## Testing Anti-Spoofing

### Test 1: Real Face ✅
1. Start app_antispoofing.py
2. Look at camera
3. Should show: **"Real"** with green box

### Test 2: Printed Photo ❌
1. Print a photo of a face
2. Hold it to camera
3. Should show: **"Fake"** with red box

### Test 3: Phone Display ❌
1. Display face photo on phone
2. Point phone at camera
3. Should show: **"Fake"** with red box

---

## What's the Difference?

| App | Anti-Spoofing | Liveness | Setup Difficulty |
|-----|---------------|----------|------------------|
| app_antispoofing.py | ✅ **Best** | ❌ | ⭐ Easy |
| app_enhanced.py | ❌ | ❌ | ⭐ Easy |
| app.py | ⚠️ Basic | ✅ **Best** | ⭐⭐⭐ Hard |

**Recommendation:** Start with `app_antispoofing.py` for best results with easy setup!

---

## Guides

- **ANTISPOOFING_GUIDE.md** - Complete anti-spoofing documentation
- **FEATURES.md** - Detailed feature breakdown  
- **INSTALL_GUIDE.md** - Installation for InsightFace
- **README.md** - Full project documentation

---

## Quick Commands

```bash
# Anti-spoofing (recommended)
streamlit run app_antispoofing.py

# Enhanced detection
streamlit run app_enhanced.py

# Full version (after setup)
streamlit run app.py

# Basic version
streamlit run app_simple.py
```

---

**Current Status:** ✅ Anti-spoofing app running at `http://localhost:8501`

**Try it now!** Test with real face vs printed photo 🎯

