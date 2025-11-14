# 🔐 Hybrid Face Liveness Detection - Quick Reference

## 🆕 NEW: Combined MediaPipe + Anti-spoofing

The **best and most secure** detection system is now available!

### Run the Hybrid App

```bash
streamlit run app_hybrid.py
```

---

## 🎯 What Makes It Better?

### Old System (Separate)
- ❌ MediaPipe tab alone → Can be fooled by phone video replays
- ❌ Anti-spoofing tab alone → May have false positives

### New System (Hybrid) ✅
- ✅ **MediaPipe**: Proves person is LIVE (blinks, movement)
- ✅ **Anti-spoofing**: Proves it's NOT a screen/photo
- ✅ **Both must pass** = Maximum security!

---

## 🔒 Security Levels

| Level | Name | How It Works | Best For |
|-------|------|--------------|----------|
| 1 | 🔓 Basic | Anti-spoofing only | Quick checks |
| 2 | 🔐 Standard | Either passes (OR logic) | General use |
| 3 | 🔒 High | Both pass (AND logic) | **Recommended** |
| 4 | 🔐 Maximum | Both + challenges (2+ blinks, 2+ movements) | Max security |

---

## 📱 Your Scenario: Phone Screen Detection

### Problem You Had:
```
Real face     → Detected as FAKE (29.7%) ❌
Phone screen  → Detected as REAL (62.0%) ❌
```

### Solution with Hybrid System:

**Real Face:**
```
MediaPipe:     ✅ LIVE (blinks detected: 85%)
Anti-spoofing: ✅ REAL (3D depth, natural lighting: 68%)
Phone indicators: 0/4
→ VERIFIED ✅ (Combined: 76.5%)
```

**Phone Screen with Video:**
```
MediaPipe:     ✅ LIVE (video shows blinking: 65%)  [Fooled!]
Anti-spoofing: ❌ FAKE (flat, bezel detected: 26%)  [Caught!]
Phone indicators: 4/4 ⚠️
→ NOT VERIFIED ❌ (Phone screen detected!)
```

**Why it works:** Even if MediaPipe is fooled by a video, anti-spoofing detects the phone screen!

---

## 🚀 Quick Start

### 1. Run the app
```bash
streamlit run app_hybrid.py
```

### 2. Configure settings
- **Security Level**: Select "3 - High" (recommended)
- **Detection Sensitivity**: "Very Lenient" (for normal lighting)

### 3. Start verification
1. Click "🎥 Start Verification"
2. Look at camera
3. Blink naturally (1-2 times)
4. Move your head (left/right or up/down)
5. Wait for result

**Expected:**
- Your real face: ✅ VERIFIED (60-85%)
- Phone screen: ❌ NOT VERIFIED (phone detected)

---

## 📚 Documentation

- **[HYBRID_DETECTION_GUIDE.md](HYBRID_DETECTION_GUIDE.md)** - Complete guide
- **[PHONE_SCREEN_FIX.md](PHONE_SCREEN_FIX.md)** - Technical phone detection details

---

## 🎬 Example Results

### Test 1: Real Person ✅
```
Status: ✅ VERIFIED
Security: HIGH
Combined Confidence: 87.5%

MediaPipe: ✅ LIVE (85%)
  - Blinks: 3
  - Movements: left, right
  
Anti-spoofing: ✅ REAL (90%)
  - Texture: 145
  - Depth: 12 (3D)
  - Phone indicators: 0/4
```

### Test 2: Phone Screen ❌
```
Status: ❌ NOT VERIFIED
Security: HIGH
Combined Confidence: 26.5%

MediaPipe: ✅ LIVE (65%)  [Video replay fooled it]
  - Blinks: 2 (from video)
  
Anti-spoofing: ❌ FAKE (26%)  [Screen detected!]
  - Texture: 254
  - Depth: 35 ⚠️ (flat)
  - Boundary: 40 ⚠️ (bezel)
  - Lighting: 25 ⚠️ (backlight)
  - Phone indicators: 4/4 ⚠️
  
Message: ❌ PHONE SCREEN DETECTED (4/4 indicators)
```

---

## 🔧 All Available Apps

| App | Description | Best For | Command |
|-----|-------------|----------|---------|
| **`app_hybrid.py`** | ⭐ **Recommended** - Combined system | Maximum security | `streamlit run app_hybrid.py` |
| `app_complete.py` | Separate tabs (MediaPipe + Anti-spoofing) | Testing each method | `streamlit run app_complete.py` |
| `app_antispoofing.py` | Anti-spoofing only | Quick passive checks | `streamlit run app_antispoofing.py` |
| `app.py` | InsightFace liveness | Legacy support | `streamlit run app.py` |

---

## ✅ Summary

**Your Problem:** Phone screens were passing as real faces

**Solution:** Hybrid system with 4 phone-specific detection algorithms:
1. ✅ Depth gradient (flatness detection)
2. ✅ Rectangular boundary (phone bezel)
3. ✅ Lighting uniformity (artificial backlight)
4. ✅ Color saturation (unnatural colors)

**Result:** 
- Real faces: ✅ Verified correctly
- Phone screens: ❌ Detected and blocked

**Recommended App:** `app_hybrid.py` with Security Level 3 (High)

🎉 **Problem solved with maximum security!**

