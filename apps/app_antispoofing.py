import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import threading
from queue import Queue
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import TextureAntiSpoofing, AntiSpoofing, FaceDetector, ONNX_AVAILABLE

st.set_page_config(page_title='Anti-Spoofing Face Detection', layout='wide')

# Initialize session state
if 'detection_log' not in st.session_state:
    st.session_state.detection_log = []
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = Queue(maxsize=2)
if 'use_onnx_model' not in st.session_state:
    st.session_state.use_onnx_model = False

@st.cache_resource
def load_face_detector():
    """Load face detector"""
    return FaceDetector()

def load_texture_antispoofing(variance_threshold, edge_threshold, confidence_threshold=0.45):
    """Load texture-based anti-spoofing (no caching - parameters change)"""
    return TextureAntiSpoofing(variance_threshold, edge_threshold, confidence_threshold)

@st.cache_resource
def load_onnx_antispoofing(model_path):
    """Load ONNX model-based anti-spoofing"""
    try:
        return AntiSpoofing(model_path)
    except Exception as e:
        st.error(f"Failed to load ONNX model: {e}")
        return None

def log_detection(num_faces, predictions):
    """Log detection results with timestamp"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'num_faces': num_faces,
        'real_count': sum([1 for p in predictions if p[0]]),
        'fake_count': sum([1 for p in predictions if not p[0]]),
        'avg_confidence': np.mean([p[1] for p in predictions]) if predictions else 0,
        'predictions': str(predictions)
    }
    st.session_state.detection_log.append(log_entry)
    
    # Save to CSV
    df = pd.DataFrame(st.session_state.detection_log)
    df.to_csv('antispoofing_log.csv', index=False)

def process_frame_texture(frame, face_detector, anti_spoof):
    """Process frame with texture-based anti-spoofing"""
    # Detect faces
    faces = face_detector.detect(frame)
    
    predictions = []
    
    # Sort faces by size (largest first) to prioritize actual faces
    if len(faces) > 0:
        faces_with_size = [(x, y, w, h, w*h) for (x, y, w, h) in faces]
        faces_with_size.sort(key=lambda f: f[4], reverse=True)
        faces = [(x, y, w, h) for (x, y, w, h, _) in faces_with_size]
    
    for (x, y, w, h) in faces:
        bbox = (x, y, x+w, y+h)
        
        # Check if real or fake
        is_real, confidence, label, scores = anti_spoof.predict(frame, bbox)
        predictions.append((is_real, confidence, label, scores))
        
        # Draw results with thicker lines
        color = (0, 255, 0) if is_real else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Display label and confidence
        text = f"{label}: {confidence:.2f}"
        cv2.putText(frame, text, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        # Display detailed scores below the face
        if 'moire' in scores:
            score_text = f"T:{scores['texture']:.0f} E:{scores['edges']:.1f} M:{scores['moire']:.1f}"
        else:
            score_text = f"Texture:{scores['texture']:.0f} Edge:{scores['edges']:.1f}"
        cv2.putText(frame, score_text, (x, y+h+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return rgb_img, predictions

def process_frame_onnx(frame, face_detector, anti_spoof):
    """Process frame with ONNX model-based anti-spoofing"""
    # Detect faces
    faces = face_detector.detect(frame)
    
    predictions = []
    for (x, y, w, h) in faces:
        bbox = (x, y, x+w, y+h)
        
        # Check if real or fake
        is_real, confidence, label = anti_spoof.predict(frame, bbox)
        predictions.append((is_real, confidence, label, {}))
        
        # Draw results
        color = (0, 255, 0) if is_real else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        text = f"{label}: {confidence:.2f}"
        cv2.putText(frame, text, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return rgb_img, predictions

class WebcamThread(threading.Thread):
    """Thread for continuous webcam capture"""
    def __init__(self, frame_queue, camera_index=0):
        threading.Thread.__init__(self)
        self.frame_queue = frame_queue
        self.camera_index = camera_index
        self.stopped = False
        
    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while not self.stopped:
            ret, frame = cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.03)  # ~30 FPS
        
        cap.release()
    
    def stop(self):
        self.stopped = True

# Title
st.title('🛡️ Anti-Spoofing Face Detection')
st.markdown('**Detect real faces vs printed photos, video replays, and masks**')

# Sidebar
with st.sidebar:
    st.header('⚙️ Settings')
    
    # Model selection
    st.subheader('Detection Method')
    
    # Check for ONNX model
    model_path = 'models/2.7_80x80_MiniFASNetV2.onnx'
    onnx_model_available = os.path.exists(model_path)
    
    if onnx_model_available:
        detection_method = st.radio(
            'Choose Method',
            ['Texture Analysis (Fast)', 'ONNX Model (Accurate)'],
            help='Texture analysis works immediately, ONNX model requires downloaded weights'
        )
        use_onnx = detection_method == 'ONNX Model (Accurate)'
    else:
        st.info('💡 Using Texture Analysis (No model download required)')
        use_onnx = False
        
        with st.expander('📥 Want ONNX Model?'):
            st.markdown("""
            **Download Silent-Face-Anti-Spoofing:**
            
            ```bash
            git clone https://github.com/minivision-ai/Silent-Face-Anti-Spoofing.git
            cd Silent-Face-Anti-Spoofing
            # Download models from releases
            # Copy .onnx files to models/ folder
            ```
            
            **Model Features:**
            - Real face detection
            - Printed photo detection
            - Video replay detection  
            - Mask detection
            """)
    
    # Texture analysis parameters
    if not use_onnx:
        st.subheader('🎛️ Detection Parameters')
        st.markdown('Adjust sensitivity for your environment:')
        
        detection_quality = st.select_slider(
            'Detection Quality',
            options=['Very Lenient', 'Lenient', 'Balanced', 'Strict'],
            value='Very Lenient',
            help='⚠️ Start with Very Lenient! Adjust only if needed'
        )
        
        # Map quality settings to parameters (includes confidence threshold)
        quality_map = {
            'Very Lenient': (50, 2.5, 0.35),
            'Lenient': (70, 3.5, 0.40),
            'Balanced': (90, 4.5, 0.45),
            'Strict': (110, 5.5, 0.50)
        }
        variance_threshold, edge_threshold, confidence_threshold = quality_map[detection_quality]
        
        st.success(f'✅ **{detection_quality} Mode**\n- Texture: {variance_threshold}\n- Edge: {edge_threshold}\n- Threshold: {confidence_threshold}')
        
        # Show current thresholds
        with st.expander('📊 Current Thresholds'):
            st.write(f'Texture Variance: {variance_threshold}')
            st.write(f'Edge Density: {edge_threshold}')
            st.info('💡 **Lenient**: Fewer false rejections, more false acceptances\n\n**Strict**: More false rejections, fewer false acceptances')
    else:
        variance_threshold = 100
        edge_threshold = 5.0
        confidence_threshold = 0.50
    
    # Detection mode
    st.subheader('Detection Mode')
    detection_mode = st.radio(
        'Mode',
        ['Single Image', 'Continuous Webcam'],
        help='Single image or live streaming'
    )
    
    # Logging
    show_logs = st.checkbox('Show Detection Logs', value=True)
    
    if st.button('Clear Logs'):
        st.session_state.detection_log = []
        if os.path.exists('antispoofing_log.csv'):
            os.remove('antispoofing_log.csv')
        st.success('Logs cleared!')
    
    # Statistics
    st.markdown('---')
    st.markdown('### 📊 Statistics')
    if st.session_state.detection_log:
        total_detections = len(st.session_state.detection_log)
        total_real = sum([log['real_count'] for log in st.session_state.detection_log])
        total_fake = sum([log['fake_count'] for log in st.session_state.detection_log])
        
        st.metric('Total Detections', total_detections)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Real', total_real, delta='✓')
        with col2:
            st.metric('Fake', total_fake, delta='⚠', delta_color='inverse')

# Load models
face_detector = load_face_detector()

if use_onnx:
    anti_spoof = load_onnx_antispoofing(model_path)
    if anti_spoof is None:
        st.error('Failed to load ONNX model. Falling back to texture analysis.')
        use_onnx = False
        anti_spoof = load_texture_antispoofing(variance_threshold, edge_threshold, confidence_threshold)
else:
    anti_spoof = load_texture_antispoofing(variance_threshold, edge_threshold, confidence_threshold)

# Main content
if detection_mode == 'Single Image':
    st.session_state.webcam_running = False
    
    uploaded_file = st.file_uploader('Upload an image', type=['jpg', 'jpeg', 'png'])
    use_webcam_snapshot = st.checkbox('Or capture from webcam')
    
    frame = None
    
    if use_webcam_snapshot:
        st.info('Click Capture Image when ready.')
        cam = st.camera_input('Capture Image')
        if cam is not None:
            file_bytes = np.asarray(bytearray(cam.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
    
    elif uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
    
    if frame is not None:
        with st.spinner('Analyzing for spoofing...'):
            if use_onnx:
                rgb_img, predictions = process_frame_onnx(frame, face_detector, anti_spoof)
            else:
                rgb_img, predictions = process_frame_texture(frame, face_detector, anti_spoof)
        
        if len(predictions) == 0:
            st.warning('No face detected. Please try again.')
            log_detection(0, [])
        else:
            st.image(rgb_img, channels='RGB', caption=f'Detected {len(predictions)} face(s).')
            
            # Log detection
            log_detection(len(predictions), predictions)
            
            # Display results
            st.markdown('### 🔍 Detection Results')
            
            cols = st.columns(min(len(predictions), 4))
            for idx, (col, (is_real, confidence, label, scores)) in enumerate(zip(cols, predictions)):
                with col:
                    if is_real:
                        st.success(f'**Face {idx+1}: {label}**')
                    else:
                        st.error(f'**Face {idx+1}: {label}**')
                    
                    st.metric('Confidence', f'{confidence:.1%}')
                    
                    if scores:  # Texture analysis scores
                        with st.expander('📊 Detailed Analysis'):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Basic Metrics:**")
                                st.write(f"Texture: {scores['texture']:.1f}")
                                st.write(f"Edges: {scores['edges']:.1f}%")
                                st.write(f"Color: {scores['color']:.1f}")
                            if 'moire' in scores:
                                with col2:
                                    st.write("**Screen Detection:**")
                                    st.write(f"Moiré: {scores['moire']:.1f}")
                                    st.write(f"Reflection: {scores['reflection']:.1f}%")
                                    st.write(f"Noise: {scores['noise']:.1f}")
                                    
                                # Add interpretation
                                st.markdown("---")
                                warnings = []
                                if scores['reflection'] > 5:
                                    warnings.append("⚠️ High reflection detected (screen indicator)")
                                if scores['moire'] > 30:
                                    warnings.append("⚠️ Moiré pattern detected (screen display)")
                                if scores['noise'] < 2:
                                    warnings.append("⚠️ Low noise (possible compression)")
                                if scores['texture'] < 60:
                                    warnings.append("⚠️ Low texture (possible fake)")
                                
                                # Debug info
                                st.caption(f"🔍 Debug: M:{scores['moire']:.1f} R:{scores['reflection']:.1f}% N:{scores['noise']:.1f}")
                                    
                                if warnings:
                                    for w in warnings:
                                        st.warning(w)
                                else:
                                    st.success("✅ No screen indicators detected")
            
            # Overall summary
            real_count = sum([1 for p in predictions if p[0]])
            fake_count = sum([1 for p in predictions if not p[0]])
            
            if fake_count == 0:
                st.success(f'✅ All {len(predictions)} face(s) verified as REAL!')
            elif real_count == 0:
                st.error(f'❌ All {len(predictions)} face(s) detected as FAKE/SPOOFED!')
            else:
                st.warning(f'⚠️ Mixed results: {real_count} real, {fake_count} fake')

else:  # Continuous Webcam
    st.markdown('### 📹 Live Anti-Spoofing Detection')
    
    # Control buttons at the top
    button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
    
    with button_col1:
        if st.button('🎥 Start Stream', disabled=st.session_state.webcam_running, use_container_width=True):
            st.session_state.webcam_running = True
            st.session_state.frame_queue = Queue(maxsize=2)
            webcam_thread = WebcamThread(st.session_state.frame_queue)
            webcam_thread.daemon = True
            webcam_thread.start()
            st.session_state.webcam_thread = webcam_thread
            st.rerun()
    
    with button_col2:
        if st.button('⏹️ Stop Stream', disabled=not st.session_state.webcam_running, type='primary', use_container_width=True):
            st.session_state.webcam_running = False
            if hasattr(st.session_state, 'webcam_thread'):
                st.session_state.webcam_thread.stop()
            st.rerun()
    
    st.markdown('---')
    
    # Video display area
    video_placeholder = st.empty()
    stats_placeholder = st.empty()
    
    if st.session_state.webcam_running:
        # Status indicator with stop reminder
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            st.success('🔴 **LIVE** - Real-time anti-spoofing detection active')
        with status_col2:
            st.markdown('**Click ⏹️ Stop to end**')
        
        frame_count = 0
        detection_interval = 3
        
        while st.session_state.webcam_running:
            if not st.session_state.frame_queue.empty():
                frame = st.session_state.frame_queue.get()
                frame_count += 1
                
                if frame_count % detection_interval == 0:
                    if use_onnx:
                        rgb_img, predictions = process_frame_onnx(frame, face_detector, anti_spoof)
                    else:
                        rgb_img, predictions = process_frame_texture(frame, face_detector, anti_spoof)
                    
                    video_placeholder.image(rgb_img, channels='RGB', use_container_width=True)
                    
                    if len(predictions) > 0:
                        real_count = sum([1 for p in predictions if p[0]])
                        fake_count = sum([1 for p in predictions if not p[0]])
                        
                        if fake_count > 0:
                            stats_placeholder.error(f'🚨 SPOOFING DETECTED! {fake_count} fake face(s), {real_count} real')
                        else:
                            stats_placeholder.success(f'✅ All Verified: {real_count} real face(s) detected')
                        
                        # Log periodically
                        if frame_count % 30 == 0:
                            log_detection(len(predictions), predictions)
                    else:
                        stats_placeholder.info('No faces detected')
            else:
                time.sleep(0.01)
    else:
        st.info('👆 Click "Start" to begin live detection')

# Display logs
if show_logs and st.session_state.detection_log:
    st.markdown('---')
    st.markdown('### 📋 Detection Logs')
    
    df = pd.DataFrame(st.session_state.detection_log)
    st.dataframe(df.tail(10), use_container_width=True)
    
    csv = df.to_csv(index=False)
    st.download_button(
        label='📥 Download Log',
        data=csv,
        file_name=f'antispoofing_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Footer
st.markdown('---')
st.markdown(f'''
### 📌 Active Features:
- {'✅ ONNX Model Detection' if use_onnx else '✅ Texture-Based Detection'}
- ✅ Multi-face anti-spoofing
- ✅ Real-time webcam streaming
- ✅ Automatic logging
- ✅ Detects: printed photos, video replays, masks

**Detection Method:** {'ONNX Model (High Accuracy)' if use_onnx else 'Texture Analysis (Fast & Reliable)'}
''')

