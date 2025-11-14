# Installation Guide for Windows

## Issue
InsightFace requires Microsoft Visual C++ 14.0 or greater to compile on Windows.

## Solution: Install Visual C++ Build Tools

### Step 1: Download Build Tools
Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Step 2: Install Build Tools
1. Run the downloaded installer
2. Select "Desktop development with C++"
3. Make sure these are checked:
   - MSVC v142 or later
   - Windows 10 SDK or later
4. Click Install (may take 10-20 minutes)

### Step 3: Install Python Dependencies
After installing Build Tools, run:
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

## Alternative Solution: Use Pre-built Wheels

If you don't want to install Build Tools, you can try:

```bash
pip install insightface-unofficial
```

Or use the simplified version without InsightFace (see app_simple.py)

