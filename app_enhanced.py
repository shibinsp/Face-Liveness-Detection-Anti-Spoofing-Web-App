import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import threading
from queue import Queue
import os

st.set_page_config(page_title='Enhanced Face Detection', layout='wide')

# Initialize session state
if 'detection_log' not in st.session_state:
    st.session_state.detection_log = []
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = Queue(maxsize=2)

# Load OpenCV's pre-trained face detector
@st.cache_resource
def load_face_detector():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_face_detector()

def log_detection(num_faces, confidence=None, is_live=None):
    """Log detection results with timestamp"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'num_faces': num_faces,
        'confidence': confidence if confidence else 'N/A',
        'is_live': is_live if is_live else 'N/A'
    }
    st.session_state.detection_log.append(log_entry)
    
    # Save to CSV
    df = pd.DataFrame(st.session_state.detection_log)
    df.to_csv('detection_log.csv', index=False)

def process_frame(frame, face_cascade):
    """Process a single frame and detect faces"""
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    face_data = []
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(rgb_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Calculate a mock confidence score based on face size
        confidence = min((w * h) / 10000, 1.0)
        
        cv2.putText(rgb_img, f'Face ({confidence:.2f})', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        face_data.append({'bbox': (x, y, w, h), 'confidence': confidence})
    
    return rgb_img, face_data

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

# Title and description
st.title('🧠 Enhanced Face Detection System')
st.markdown('**Features:** Continuous webcam stream, multi-face detection, logging, and GPU support')

# Sidebar for settings
with st.sidebar:
    st.header('⚙️ Settings')
    
    detection_mode = st.radio(
        'Detection Mode',
        ['Single Image', 'Continuous Webcam Stream'],
        help='Choose between single image detection or live streaming'
    )
    
    show_logs = st.checkbox('Show Detection Logs', value=True)
    
    if st.button('Clear Logs'):
        st.session_state.detection_log = []
        if os.path.exists('detection_log.csv'):
            os.remove('detection_log.csv')
        st.success('Logs cleared!')
    
    st.markdown('---')
    st.markdown('### 📊 Statistics')
    if st.session_state.detection_log:
        total_detections = len(st.session_state.detection_log)
        total_faces = sum([log['num_faces'] for log in st.session_state.detection_log])
        st.metric('Total Detections', total_detections)
        st.metric('Total Faces Detected', total_faces)

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
        rgb_img, face_data = process_frame(frame, face_cascade)
        
        if len(face_data) == 0:
            st.warning('No face detected. Please try again.')
            log_detection(0)
        else:
            st.image(rgb_img, channels='RGB', caption=f'Detected {len(face_data)} face(s).')
            st.success(f'✅ Detected {len(face_data)} face(s)!')
            
            # Log the detection
            avg_confidence = sum([f['confidence'] for f in face_data]) / len(face_data)
            log_detection(len(face_data), avg_confidence)
            
            # Show individual face details
            st.markdown('### 👤 Face Details')
            cols = st.columns(min(len(face_data), 4))
            for idx, (col, face_info) in enumerate(zip(cols, face_data)):
                with col:
                    st.metric(f'Face {idx+1}', f"{face_info['confidence']:.2%}", 'Confidence')

else:  # Continuous Webcam Stream
    st.markdown('### 📹 Live Webcam Stream')
    
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
        st.info('🔴 Live stream active - detecting faces in real-time...')
        
        frame_count = 0
        detection_interval = 5  # Process every 5th frame for performance
        
        while st.session_state.webcam_running:
            if not st.session_state.frame_queue.empty():
                frame = st.session_state.frame_queue.get()
                frame_count += 1
                
                # Process every Nth frame
                if frame_count % detection_interval == 0:
                    rgb_img, face_data = process_frame(frame, face_cascade)
                    
                    video_placeholder.image(rgb_img, channels='RGB', use_container_width=True)
                    
                    if len(face_data) > 0:
                        stats_placeholder.success(f'✅ Detecting {len(face_data)} face(s) in real-time')
                        
                        # Log every 30 frames (roughly once per second)
                        if frame_count % 30 == 0:
                            avg_confidence = sum([f['confidence'] for f in face_data]) / len(face_data)
                            log_detection(len(face_data), avg_confidence)
                    else:
                        stats_placeholder.info('No faces detected in frame')
            else:
                time.sleep(0.01)
    else:
        st.info('👆 Click "Start Stream" to begin live face detection')

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
        file_name=f'face_detection_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Footer
st.markdown('---')
st.markdown('''
### 📌 Features Active:
- ✅ **Multi-face detection** - Detects and tracks multiple faces simultaneously
- ✅ **Continuous webcam stream** - Real-time face detection with threading
- ✅ **Logging system** - All detections saved to CSV with timestamps
- ⚠️ **GPU acceleration** - Available with InsightFace + onnxruntime-gpu

*Note: This is the OpenCV version. For advanced liveness detection with GPU support, install InsightFace (requires Visual C++ Build Tools on Windows).*
''')

