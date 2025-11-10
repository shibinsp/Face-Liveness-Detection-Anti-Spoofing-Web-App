# 📦 Installation Guide

Complete installation instructions for all versions of the Face Liveness Detection app.

## Table of Contents
- [Quick Install (Recommended)](#quick-install-recommended)
- [Full Install (InsightFace)](#full-install-insightface)
- [Troubleshooting](#troubleshooting)
- [Verification](#verification)

---

## Quick Install (Recommended)

**Time: 2-5 minutes**

Works for:
- ✅ `app_antispoofing.py` (Anti-spoofing detection)
- ✅ `app_enhanced.py` (Enhanced detection)
- ✅ `app_simple.py` (Basic detection)

### Step 1: Install Python

Ensure Python 3.8+ is installed:
```bash
python --version
# Should show Python 3.8.0 or higher
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Install Dependencies

```bash
pip install streamlit opencv-python numpy pandas
```

### Step 3: Run the App

```bash
# Anti-spoofing (recommended)
streamlit run app_antispoofing.py

# OR enhanced version
streamlit run app_enhanced.py

# OR simple version
streamlit run app_simple.py
```

### Step 4: Test

- Browser should open automatically to `http://localhost:8501`
- If not, open the URL manually
- Try capturing a face from webcam

**✅ Done! You're ready to go.**

---

## Optional: ONNX Models

For higher anti-spoofing accuracy (95%+):

### Step 1: Install ONNX Runtime

```bash
pip install onnxruntime
```

### Step 2: Download Models

**Option A: Direct Download**
1. Visit: https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/releases
2. Download: `2.7_80x80_MiniFASNetV2.onnx`
3. Place in: `models/` directory

**Option B: Clone Repository**
```bash
git clone https://github.com/minivision-ai/Silent-Face-Anti-Spoofing.git
cd Silent-Face-Anti-Spoofing
# Copy models from resources/anti_spoof_models/ to your project/models/
```

### Step 3: Enable in App

Run `app_antispoofing.py` and select "ONNX Model (Accurate)" in sidebar.

---

## Full Install (InsightFace)

**Time: 15-30 minutes**

Works for:
- ✅ `app.py` (Full liveness detection with InsightFace)

### Windows Installation

#### Step 1: Install Visual C++ Build Tools

**Why needed:** InsightFace requires compilation on Windows

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select **"Desktop development with C++"**
4. Check these components:
   - MSVC v142 (or latest)
   - Windows 10 SDK (or latest)
5. Click Install
6. Wait 10-20 minutes
7. Restart computer

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- InsightFace and all dependencies
- May take 5-10 minutes
- Downloads ~300MB of packages

#### Step 3: First Run (Downloads Models)

```bash
streamlit run app.py
```

First run will download InsightFace models (~300MB):
- This happens automatically
- Takes 2-5 minutes depending on internet speed
- Only needed once

#### Step 4: Verify

- App should open in browser
- Try uploading an image or using webcam
- Should see liveness scores

**✅ Installation complete!**

---

### Linux Installation

#### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-dev build-essential cmake

# Install Python packages
pip install -r requirements.txt

# Run app
streamlit run app.py
```

#### CentOS/RHEL

```bash
# Install system dependencies
sudo yum install -y python3-devel gcc gcc-c++ cmake

# Install Python packages
pip install -r requirements.txt

# Run app
streamlit run app.py
```

---

### macOS Installation

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake

# Install Python packages
pip install -r requirements.txt

# Run app
streamlit run app.py
```

---

## GPU Acceleration (Optional)

For faster processing with NVIDIA GPU:

### Prerequisites
- NVIDIA GPU (GTX 1050 or better)
- CUDA Toolkit 11.8+ or 12.x
- Windows/Linux (not macOS)

### Step 1: Install CUDA

Download from: https://developer.nvidia.com/cuda-downloads

Follow installer instructions for your OS.

### Step 2: Install GPU Runtime

```bash
# Uninstall CPU version
pip uninstall onnxruntime

# Install GPU version
pip install onnxruntime-gpu
```

### Step 3: Verify

```bash
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

Should show: `['CUDAExecutionProvider', 'CPUExecutionProvider']`

### Step 4: Enable in App

Run `app.py` and check "Use GPU Acceleration" in sidebar.

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'insightface'"

**Problem:** InsightFace not installed

**Solution:**
```bash
# Use quick install apps instead
streamlit run app_antispoofing.py

# OR install InsightFace
pip install -r requirements.txt
```

#### 2. "Microsoft Visual C++ 14.0 or greater is required"

**Problem:** Build tools not installed (Windows only)

**Solution:**
1. Install Visual C++ Build Tools (see Step 1 above)
2. Restart computer
3. Try installation again

#### 3. "ModuleNotFoundError: No module named 'cv2'"

**Problem:** OpenCV not installed

**Solution:**
```bash
pip install opencv-python
```

#### 4. Webcam not working

**Problem:** Camera permissions or driver issues

**Solutions:**
- Check browser permissions for camera access
- Close other apps using camera
- Try different camera index (edit code: `camera_index=1`)
- Update camera drivers

#### 5. "Streamlit not found"

**Problem:** Streamlit not installed or not in PATH

**Solution:**
```bash
pip install --upgrade streamlit

# If still not working, use full path:
python -m streamlit run app_antispoofing.py
```

#### 6. Port 8501 already in use

**Problem:** Another Streamlit app running

**Solution:**
```bash
# Kill existing process
# Windows:
taskkill /F /IM streamlit.exe

# Linux/Mac:
pkill -f streamlit

# OR use different port:
streamlit run app_antispoofing.py --server.port 8502
```

#### 7. Slow performance

**Solutions:**
- Reduce video resolution (edit code)
- Increase detection_interval (edit code)
- Close other applications
- Use GPU acceleration (if available)
- Use simpler app version (app_simple.py)

#### 8. Models not downloading (InsightFace)

**Problem:** Network issues or firewall blocking

**Solution:**
```bash
# Manual download
# Visit: https://github.com/deepinsight/insightface/releases
# Download buffalo_l model
# Place in: ~/.insightface/models/buffalo_l/
```

---

## Verification

### Test Installation

**1. Check Python Packages:**
```bash
python -c "import streamlit; import cv2; import numpy; import pandas; print('✅ All packages installed')"
```

**2. Test Basic App:**
```bash
streamlit run app_simple.py
```

**3. Test Anti-Spoofing:**
```bash
streamlit run app_antispoofing.py
```

**4. Test InsightFace (if installed):**
```bash
streamlit run app.py
```

### Expected Behavior

- Browser opens automatically
- App loads without errors
- Webcam permission requested
- Face detection works
- No error messages in terminal

---

## Update Instructions

### Update Packages

```bash
# Update all packages
pip install --upgrade streamlit opencv-python numpy pandas

# Update InsightFace (if installed)
pip install --upgrade insightface onnxruntime
```

### Pull Latest Code

```bash
git pull origin main
```

---

## Uninstallation

### Remove Packages

```bash
# Remove core packages
pip uninstall streamlit opencv-python numpy pandas

# Remove InsightFace (if installed)
pip uninstall insightface onnxruntime
```

### Remove Models

```bash
# Windows
rmdir /s %USERPROFILE%\.insightface

# Linux/Mac
rm -rf ~/.insightface
```

### Remove Project

```bash
# Delete project directory
cd ..
rm -rf Face-Liveness-Detection-Anti-Spoofing-Web-App
```

---

## System Requirements

### Minimum
- **OS:** Windows 10, Ubuntu 18.04, macOS 10.14
- **CPU:** Any modern processor
- **RAM:** 4GB
- **Storage:** 2GB free space
- **Python:** 3.8+

### Recommended
- **OS:** Windows 11, Ubuntu 20.04+, macOS 11+
- **CPU:** Intel i5 / AMD Ryzen 5 or better
- **RAM:** 8GB+
- **Storage:** 5GB free space
- **Python:** 3.9+
- **GPU:** NVIDIA GTX 1050+ (optional)

### For GPU Acceleration
- **GPU:** NVIDIA GPU with CUDA support
- **VRAM:** 2GB+
- **CUDA:** 11.8+ or 12.x
- **Drivers:** Latest NVIDIA drivers

---

## Next Steps

After installation:

1. **Read Documentation:**
   - `README.md` - Overview
   - `QUICK_START.md` - Quick guide
   - `ANTISPOOFING_GUIDE.md` - Anti-spoofing details
   - `FEATURES.md` - Feature breakdown

2. **Try Different Apps:**
   - Start with `app_antispoofing.py`
   - Explore `app_enhanced.py`
   - Advanced users: `app.py`

3. **Test Features:**
   - Single image mode
   - Continuous webcam mode
   - Multi-face detection
   - Log analysis

4. **Customize:**
   - Adjust thresholds
   - Modify parameters
   - Add custom features

---

## Support

**Having issues?**

1. Check this installation guide
2. Review troubleshooting section
3. Check documentation files
4. Verify system requirements
5. Test with simple version first

**Still stuck?**
- Review error messages carefully
- Search for specific errors online
- Check package versions
- Try fresh installation

---

## Version Information

- **Python:** 3.8+ required, 3.9+ recommended
- **Streamlit:** 1.20.0+
- **OpenCV:** 4.7.0+
- **NumPy:** 1.24.0+
- **Pandas:** 2.0.0+
- **InsightFace:** 0.7.0+ (optional)
- **ONNX Runtime:** 1.14.0+ (optional)

---

**Ready to start?** Run `streamlit run app_antispoofing.py` 🚀

