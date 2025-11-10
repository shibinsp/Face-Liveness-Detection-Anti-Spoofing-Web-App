# Models Directory

## ONNX Anti-Spoofing Models

Place your Silent-Face-Anti-Spoofing ONNX models here.

### Recommended Models

1. **2.7_80x80_MiniFASNetV2.onnx** (Recommended)
   - Size: ~5MB
   - Input: 80×80 RGB
   - Best balance of speed and accuracy

2. **4_0_0_80x80_MiniFASNetV1SE.onnx** (Alternative)
   - Size: ~7MB
   - Input: 80×80 RGB
   - Higher accuracy, slightly slower

### How to Download

**Option 1: From GitHub Releases**
```bash
# Visit: https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/releases
# Download the model files
# Copy them to this directory
```

**Option 2: Clone Repository**
```bash
git clone https://github.com/minivision-ai/Silent-Face-Anti-Spoofing.git
cd Silent-Face-Anti-Spoofing

# Models are typically in: resources/anti_spoof_models/
# Copy the .onnx files to this directory
```

### Expected Files

After download, this directory should contain:
```
models/
├── README.md (this file)
├── 2.7_80x80_MiniFASNetV2.onnx
└── 4_0_0_80x80_MiniFASNetV1SE.onnx (optional)
```

### Model Information

**Input Format:**
- Shape: (1, 3, 80, 80)
- Type: float32
- Range: [-1, 1] (normalized)
- Color: RGB

**Output Format:**
- Shape: (1, 2)
- Type: float32
- Values: [fake_score, real_score]

**Detection Capabilities:**
- ✅ Real faces
- ✅ Printed photos
- ✅ Video replays (phone/screen)
- ✅ Mask attacks
- ✅ 3D models

### Usage in App

Once models are placed here, the app will automatically detect them:

1. Run: `streamlit run app_antispoofing.py`
2. In sidebar, select "ONNX Model (Accurate)"
3. Model loads automatically
4. Higher accuracy anti-spoofing enabled!

### Troubleshooting

**"Model not found" error:**
- Verify .onnx file is in this directory
- Check filename matches exactly: `2.7_80x80_MiniFASNetV2.onnx`
- Ensure file isn't corrupted (re-download if needed)

**"Failed to load ONNX model" error:**
- Install onnxruntime: `pip install onnxruntime`
- Check Python version compatibility (3.7+)
- Verify model file size is correct (~5MB)

### License

The Silent-Face-Anti-Spoofing models are licensed under their respective terms.
Please review the original repository for license details:
https://github.com/minivision-ai/Silent-Face-Anti-Spoofing

---

**Note:** The application works without ONNX models using texture analysis.
ONNX models provide higher accuracy but require download.

