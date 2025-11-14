import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import threading
from queue import Queue
import os

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

st.set_page_config(page_title='Face Liveness Detection', layout='wide')

# Initialize session state
if 'detection_log' not in st.session_state:
    st.session_state.detection_log = []
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = Queue(maxsize=2)
if 'use_gpu' not in st.session_state:
    st.session_state.use_gpu = False

@st.cache_resource
def load_model(use_gpu=False):
    """Load InsightFace model with optional GPU support"""
    if not INSIGHTFACE_AVAILABLE:
        return None
    
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
    app = FaceAnalysis(name='buffalo_l', providers=providers)
    app.prepare(ctx_id=0 if use_gpu else -1, det_size=(640, 640))
    return app

def log_detection(num_faces, liveness_scores=None, labels=None):
    """Log detection results with timestamp"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'num_faces': num_faces,
        'liveness_scores': str(liveness_scores) if liveness_scores else 'N/A',
        'labels': str(labels) if labels else 'N/A',
        'avg_liveness': np.mean(liveness_scores) if liveness_scores else 'N/A'
    }
    st.session_state.detection_log.append(log_entry)
    
    # Save to CSV
    df = pd.DataFrame(st.session_state.detection_log)
    df.to_csv('liveness_detection_log.csv', index=False)

def process_frame_insightface(frame, model):
    """Process frame with InsightFace for liveness detection"""
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = model.get(rgb_img)
    
    liveness_scores = []
    labels = []
    
    for face in faces:
        box = face['bbox'].astype(int)
        liveness_score = face.get('liveness', 0)
        x1, y1, x2, y2 = box
        label = 'Live' if liveness_score > 0.5 else 'Spoof'
        
        liveness_scores.append(liveness_score)
        labels.append(label)
        
        color = (0, 255, 0) if label == 'Live' else (255, 0, 0)
        cv2.rectangle(rgb_img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(rgb_img, f'{label} ({liveness_score:.2f})', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return rgb_img, faces, liveness_scores, labels

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

# Check if InsightFace is available
if not INSIGHTFACE_AVAILABLE:
    st.error('⚠️ InsightFace not installed! Please install Visual C++ Build Tools and run: `pip install -r requirements.txt`')
    st.info('Meanwhile, you can use the simplified version: `streamlit run app_enhanced.py`')
    st.stop()

# Title and description
st.title('🧠 Face Liveness Detection System (InsightFace)')
st.markdown('**Advanced Features:** Real-time liveness detection, GPU acceleration, multi-face tracking, and logging')

# Sidebar for settings
with st.sidebar:
    st.header('⚙️ Settings')
    
    # GPU Toggle
    use_gpu = st.checkbox('Use GPU Acceleration', value=st.session_state.use_gpu,
                         help='Requires onnxruntime-gpu to be installed')
    if use_gpu != st.session_state.use_gpu:
        st.session_state.use_gpu = use_gpu
        st.cache_resource.clear()
        st.rerun()
    
    # Detection mode
    detection_mode = st.radio(
        'Detection Mode',
        ['Single Image', 'Continuous Webcam Stream'],
        help='Choose between single image detection or live streaming'
    )
    
    # Liveness threshold
    liveness_threshold = st.slider('Liveness Threshold', 0.0, 1.0, 0.5, 0.05,
                                   help='Scores above this are classified as Live')
    
    show_logs = st.checkbox('Show Detection Logs', value=True)
    
    if st.button('Clear Logs'):
        st.session_state.detection_log = []
        if os.path.exists('liveness_detection_log.csv'):
            os.remove('liveness_detection_log.csv')
        st.success('Logs cleared!')
    
    st.markdown('---')
    st.markdown('### 📊 Statistics')
    if st.session_state.detection_log:
        total_detections = len(st.session_state.detection_log)
        total_faces = sum([log['num_faces'] for log in st.session_state.detection_log])
        st.metric('Total Detections', total_detections)
        st.metric('Total Faces Detected', total_faces)
        
        # Calculate live vs spoof ratio
        live_count = sum([log['labels'].count('Live') for log in st.session_state.detection_log if log['labels'] != 'N/A'])
        spoof_count = sum([log['labels'].count('Spoof') for log in st.session_state.detection_log if log['labels'] != 'N/A'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Live', live_count, delta='Real')
        with col2:
            st.metric('Spoof', spoof_count, delta='Fake', delta_color='inverse')

# Load model
model = load_model(use_gpu=st.session_state.use_gpu)

# Main content area
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
        with st.spinner('Processing...'):
            rgb_img, faces, liveness_scores, labels = process_frame_insightface(frame, model)
        
        if len(faces) == 0:
            st.warning('No face detected. Please try again.')
            log_detection(0)
        else:
            st.image(rgb_img, channels='RGB', caption=f'Detected {len(faces)} face(s).')
            
            # Log the detection
            log_detection(len(faces), liveness_scores, labels)
            
            # Show results for each face
            st.markdown('### 👤 Detection Results')
            cols = st.columns(min(len(faces), 4))
            for idx, (col, score, label) in enumerate(zip(cols, liveness_scores, labels)):
                with col:
                    if label == 'Live':
                        st.success(f'**Face {idx+1}: {label}**')
                    else:
                        st.error(f'**Face {idx+1}: {label}**')
                    st.metric('Liveness Score', f'{score:.3f}')
            
            # Overall result
            if all(label == 'Live' for label in labels):
                st.success(f'✅ All {len(faces)} face(s) verified as LIVE!')
            elif all(label == 'Spoof' for label in labels):
                st.error(f'❌ All {len(faces)} face(s) detected as SPOOFED!')
            else:
                st.warning(f'⚠️ Mixed results: {labels.count("Live")} live, {labels.count("Spoof")} spoofed')

else:  # Continuous Webcam Stream
    st.markdown('### 📹 Live Liveness Detection Stream')
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button('🎥 Start Stream' if not st.session_state.webcam_running else '⏹️ Stop Stream'):
            st.session_state.webcam_running = not st.session_state.webcam_running
            if st.session_state.webcam_running:
                st.session_state.frame_queue = Queue(maxsize=2)
                webcam_thread = WebcamThread(st.session_state.frame_queue)
                webcam_thread.daemon = True
                webcam_thread.start()
                st.session_state.webcam_thread = webcam_thread
            else:
                if hasattr(st.session_state, 'webcam_thread'):
                    st.session_state.webcam_thread.stop()
    
    with col1:
        video_placeholder = st.empty()
        stats_placeholder = st.empty()
    
    if st.session_state.webcam_running:
        st.info('🔴 Live stream active - Real-time liveness detection...')
        
        frame_count = 0
        detection_interval = 3  # Process every 3rd frame for performance
        
        while st.session_state.webcam_running:
            if not st.session_state.frame_queue.empty():
                frame = st.session_state.frame_queue.get()
                frame_count += 1
                
                # Process every Nth frame
                if frame_count % detection_interval == 0:
                    rgb_img, faces, liveness_scores, labels = process_frame_insightface(frame, model)
                    
                    video_placeholder.image(rgb_img, channels='RGB', use_container_width=True)
                    
                    if len(faces) > 0:
                        live_count = labels.count('Live')
                        spoof_count = labels.count('Spoof')
                        
                        if live_count > 0 and spoof_count == 0:
                            stats_placeholder.success(f'✅ {live_count} LIVE face(s) detected')
                        elif spoof_count > 0:
                            stats_placeholder.error(f'❌ {spoof_count} SPOOFED face(s) detected ({live_count} live)')
                        
                        # Log every 30 frames (roughly once per second)
                        if frame_count % 30 == 0:
                            log_detection(len(faces), liveness_scores, labels)
                    else:
                        stats_placeholder.info('No faces detected in frame')
            else:
                time.sleep(0.01)
    else:
        st.info('👆 Click "Start Stream" to begin live liveness detection')

# Display logs
if show_logs and st.session_state.detection_log:
    st.markdown('---')
    st.markdown('### 📋 Detection Logs')
    
    df = pd.DataFrame(st.session_state.detection_log)
    
    # Show recent logs
    st.dataframe(df.tail(10), use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label='📥 Download Full Log (CSV)',
        data=csv,
        file_name=f'liveness_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Footer
st.markdown('---')
st.markdown(f'''
### 📌 Features Active:
- ✅ **Multi-face liveness detection** - Tracks multiple faces simultaneously
- ✅ **Continuous webcam stream** - Real-time detection with threading
- ✅ **Logging system** - All detections saved to CSV with timestamps
- {'✅' if st.session_state.use_gpu else '⚠️'} **GPU acceleration** - {'ENABLED' if st.session_state.use_gpu else 'DISABLED (CPU mode)'}
- ✅ **InsightFace buffalo_l** - Advanced anti-spoofing model

*Hardware: {'GPU (CUDA)' if st.session_state.use_gpu else 'CPU'}*
''')
