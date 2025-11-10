import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import threading
from queue import Queue
import os

# Import modules
from mediapipe_liveness import MediaPipeLiveness
from anti_spoofing import TextureAntiSpoofing, FaceDetector

st.set_page_config(page_title='Complete Liveness & Anti-Spoofing Detection', layout='wide', page_icon='🛡️')

# Initialize session state
if 'detection_log' not in st.session_state:
    st.session_state.detection_log = []
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = Queue(maxsize=2)
if 'mediapipe_liveness' not in st.session_state:
    st.session_state.mediapipe_liveness = None

# Title
st.title('🛡️ Complete Face Liveness Detection System')
st.markdown('**Two-Factor Verification:** Active Liveness + Passive Anti-Spoofing')

# ============================================================================
# SIDEBAR - Configure before tabs
# ============================================================================
with st.sidebar:
    st.markdown('## ⚙️ Settings')
    
    # Tab selector hint
    st.info('👆 Switch between tabs above to use different detection methods')
    st.markdown('---')
    
    # MediaPipe Settings
    st.markdown('### 👁️ MediaPipe Settings')
    show_landmarks = st.checkbox('Show Face Mesh', value=True, key='show_landmarks')
    challenge_mode = st.checkbox('Challenge Mode', value=False, key='challenge_mode',
                                 help='Require specific actions for verification')
    
    if challenge_mode:
        st.success('**Challenge Active:** Blink AND move head in all directions')
    
    st.markdown('---')
    
    # Anti-Spoofing Settings
    st.markdown('### 🛡️ Anti-Spoofing Settings')
    detection_quality = st.select_slider(
        'Detection Quality',
        options=['Very Lenient', 'Lenient', 'Balanced', 'Strict'],
        value='Very Lenient',
        key='as_quality',
        help='⚠️ Start with Very Lenient! Adjust only if needed:\n- Very Lenient: Best for real faces in normal conditions\n- Lenient: Balanced security\n- Balanced: Higher security\n- Strict: Maximum security (may reject real faces)'
    )
    
    quality_map = {
        'Very Lenient': (50, 2.5, 0.35),
        'Lenient': (70, 3.5, 0.40),
        'Balanced': (90, 4.5, 0.45),
        'Strict': (110, 5.5, 0.50)
    }
    variance_threshold, edge_threshold, confidence_threshold = quality_map[detection_quality]
    
    st.success(f'✅ **{detection_quality} Mode**\n📊 Texture={variance_threshold} | Edge={edge_threshold} | Threshold={confidence_threshold}')
    
    st.markdown('---')
    st.markdown('### 📊 System Info')
    st.write('✅ MediaPipe: Active')
    st.write('✅ Anti-Spoofing: Active')

# Create tabs
tab1, tab2 = st.tabs(["👁️ MediaPipe Liveness", "🛡️ Anti-Spoofing Detection"])

# ============================================================================
# TAB 1: MediaPipe Liveness Detection
# ============================================================================
with tab1:
    st.header('👁️ MediaPipe Liveness Detection')
    st.markdown("""
    **Active liveness verification using:**
    - 468 facial landmarks tracking
    - Real-time blink detection (Eye Aspect Ratio)
    - Head movement detection (left, right, up, down)
    - Interactive challenges
    """)
    
    # Detection mode selection
    mp_mode = st.radio('Select Mode', ['Single Image', 'Live Detection'], horizontal=True)
    
    if mp_mode == 'Single Image':
        st.info('Upload an image or capture from webcam for analysis')
        
        uploaded_file = st.file_uploader('Upload Image', type=['jpg', 'jpeg', 'png'], key='mp_upload')
        use_camera = st.checkbox('Or use camera', key='mp_camera')
        
        frame = None
        if use_camera:
            camera_input = st.camera_input('Capture Image')
            if camera_input:
                file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
                frame = cv2.imdecode(file_bytes, 1)
        elif uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
        
        if frame is not None:
            # Initialize MediaPipe
            if st.session_state.mediapipe_liveness is None:
                with st.spinner('Initializing MediaPipe...'):
                    st.session_state.mediapipe_liveness = MediaPipeLiveness()
            
            mp_liveness = st.session_state.mediapipe_liveness
            
            # Process frame
            with st.spinner('Analyzing...'):
                processed_frame, blink_info, head_info, is_live = mp_liveness.process_frame(frame)
                liveness_score = mp_liveness.get_liveness_score()
            
            # Display result
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            st.image(rgb_frame, channels='RGB', use_container_width=True)
            
            # Show results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric('Liveness Score', f'{liveness_score:.0%}')
                if liveness_score > 0.5:
                    st.success('✅ Likely LIVE')
                else:
                    st.warning('⚠️ Static image or no interaction')
            
            with col2:
                if blink_info:
                    st.metric('Blinks Detected', blink_info['total_blinks'])
                    st.caption(f"EAR: {(blink_info['ear_left'] + blink_info['ear_right'])/2:.3f}")
            
            with col3:
                if head_info:
                    st.metric('Head Movement', head_info['movement'].upper())
                    movements = [k for k, v in head_info['movements_detected'].items() if v and k != 'neutral']
                    st.caption(f"Detected: {', '.join(movements) if movements else 'None'}")
    
    else:  # Live Detection
        st.markdown('### 📹 Real-Time Liveness Detection')
        
        # Control buttons
        button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
        
        with button_col1:
            if st.button('🎥 Start Detection', disabled=st.session_state.webcam_running, use_container_width=True, key='mp_start'):
                st.session_state.webcam_running = True
                st.rerun()
        
        with button_col2:
            if st.button('⏹️ Stop', disabled=not st.session_state.webcam_running, type='primary', use_container_width=True, key='mp_stop'):
                st.session_state.webcam_running = False
                if st.session_state.mediapipe_liveness:
                    st.session_state.mediapipe_liveness.reset_detection()
                st.rerun()
        
        st.markdown('---')
        
        # Live detection area
        if st.session_state.webcam_running:
            # Initialize MediaPipe
            if st.session_state.mediapipe_liveness is None:
                st.session_state.mediapipe_liveness = MediaPipeLiveness()
            
            mp_liveness = st.session_state.mediapipe_liveness
            
            st.success('🔴 LIVE - Perform actions: Blink and move your head')
            
            # Placeholders
            video_placeholder = st.empty()
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            # Open webcam
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Metrics placeholders
            blink_metric = metrics_col1.empty()
            ear_metric = metrics_col2.empty()
            movement_metric = metrics_col3.empty()
            score_metric = metrics_col4.empty()
            
            while st.session_state.webcam_running:
                ret, frame = cap.read()
                if not ret:
                    st.error('Failed to access camera')
                    break
                
                # Process frame
                processed_frame, blink_info, head_info, is_live = mp_liveness.process_frame(frame)
                liveness_score = mp_liveness.get_liveness_score()
                
                # Convert and display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
                
                # Update metrics
                if blink_info:
                    blink_metric.metric('👁️ Blinks', blink_info['total_blinks'])
                    ear_metric.metric('EAR', f"{(blink_info['ear_left'] + blink_info['ear_right'])/2:.3f}")
                
                if head_info:
                    movement_metric.metric('🔄 Movement', head_info['movement'].upper())
                
                score_metric.metric('✅ Liveness', f'{liveness_score:.0%}')
                
                time.sleep(0.03)  # ~30 FPS
            
            cap.release()
        else:
            st.info('👆 Click "Start Detection" to begin')

# ============================================================================
# TAB 2: Anti-Spoofing Detection
# ============================================================================
with tab2:
    st.header('🛡️ Anti-Spoofing Detection')
    st.markdown("""
    **Passive spoofing detection using:**
    - Texture analysis
    - Moiré pattern detection (screens)
    - Reflection analysis
    - Noise pattern analysis
    """)
    
    # Load detector (cache face detector, but create new anti-spoof with updated params)
    @st.cache_resource
    def load_face_detector():
        return FaceDetector()
    
    face_detector = load_face_detector()
    anti_spoof = TextureAntiSpoofing(variance_threshold, edge_threshold, confidence_threshold)
    
    # Detection mode
    as_mode = st.radio('Select Mode', ['Single Image', 'Continuous Stream'], horizontal=True, key='as_mode')
    
    if as_mode == 'Single Image':
        uploaded_file = st.file_uploader('Upload Image', type=['jpg', 'jpeg', 'png'], key='as_upload')
        use_camera = st.checkbox('Or use camera', key='as_camera')
        
        frame = None
        if use_camera:
            camera_input = st.camera_input('Capture Image', key='as_cam_input')
            if camera_input:
                file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
                frame = cv2.imdecode(file_bytes, 1)
        elif uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
        
        if frame is not None:
            with st.spinner('Analyzing for spoofing...'):
                faces = face_detector.detect(frame)
                
                if len(faces) == 0:
                    st.warning('No face detected')
                else:
                    for (x, y, w, h) in faces:
                        bbox = (x, y, x+w, y+h)
                        is_real, confidence, label, scores = anti_spoof.predict(frame, bbox)
                        
                        # Draw results
                        color = (0, 255, 0) if is_real else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                        cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    
                    # Display
                    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(rgb_img, channels='RGB', use_container_width=True)
                    
                    # Results
                    col1, col2 = st.columns(2)
                    with col1:
                        if is_real:
                            st.success(f'✅ REAL FACE - Confidence: {confidence:.1%}')
                        else:
                            st.error(f'❌ FAKE/SPOOFED - Confidence: {confidence:.1%}')
                    
                    with col2:
                        with st.expander('📊 Detailed Metrics'):
                            st.write(f"**Texture:** {scores['texture']:.1f}")
                            st.write(f"**Edges:** {scores['edges']:.1f}%")
                            st.write(f"**Moiré:** {scores['moire']:.1f}")
                            st.write(f"**Reflection:** {scores['reflection']:.1f}%")
    
    else:  # Continuous Stream
        st.markdown('### 📹 Real-Time Anti-Spoofing Stream')
        
        # Control buttons
        button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
        
        with button_col1:
            if st.button('🎥 Start Stream', disabled=st.session_state.webcam_running, use_container_width=True, key='as_start_stream'):
                st.session_state.webcam_running = True
                st.rerun()
        
        with button_col2:
            if st.button('⏹️ Stop Stream', disabled=not st.session_state.webcam_running, type='primary', use_container_width=True, key='as_stop_stream'):
                st.session_state.webcam_running = False
                st.rerun()
        
        st.markdown('---')
        
        # Live detection area
        if st.session_state.webcam_running:
            st.success('🔴 LIVE - Real-time anti-spoofing detection')
            
            # Placeholders
            video_placeholder = st.empty()
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            # Metrics placeholders
            result_metric = metrics_col1.empty()
            confidence_metric = metrics_col2.empty()
            faces_metric = metrics_col3.empty()
            
            # Open webcam
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag
            
            frame_count = 0
            detection_interval = 5  # Process every 5th frame for smoother performance
            last_prediction = None  # Cache last prediction to avoid flickering
            
            while st.session_state.webcam_running:
                ret, frame = cap.read()
                if not ret:
                    st.error('Failed to access camera')
                    break
                
                frame_count += 1
                display_frame = frame.copy()
                
                # Process every Nth frame for detection, but display every frame
                if frame_count % detection_interval == 0:
                    # Detect faces
                    faces = face_detector.detect(frame)
                    
                    if len(faces) > 0:
                        predictions = []
                        for (x, y, w, h) in faces:
                            bbox = (x, y, x+w, y+h)
                            is_real, confidence, label, scores = anti_spoof.predict(frame, bbox)
                            predictions.append((x, y, w, h, is_real, confidence, label, scores))
                        
                        last_prediction = predictions
                else:
                    # Use cached prediction for smoother display
                    if last_prediction is not None:
                        predictions = last_prediction
                    else:
                        predictions = []
                
                # Draw results on display frame
                if last_prediction:
                    for pred in last_prediction:
                        if len(pred) == 8:
                            x, y, w, h, is_real, confidence, label, scores = pred
                            
                            # Draw results
                            color = (0, 255, 0) if is_real else (0, 0, 255)
                            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 3)
                            cv2.putText(display_frame, f"{label}: {confidence:.1%}", (x, y-10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                            
                            # Display scores
                            score_text = f"T:{scores['texture']:.0f} E:{scores['edges']:.0f}"
                            cv2.putText(display_frame, score_text, (x, y+h+25),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Update metrics only when we have predictions
                    if frame_count % detection_interval == 0:
                        real_count = sum([1 for pred in last_prediction if pred[4]])
                        fake_count = len(last_prediction) - real_count
                        avg_conf = np.mean([pred[5] for pred in last_prediction])
                        
                        if fake_count > 0:
                            result_metric.error(f'🚨 SPOOFING DETECTED')
                        else:
                            result_metric.success(f'✅ ALL VERIFIED')
                        
                        confidence_metric.metric('Avg Confidence', f'{avg_conf:.1%}')
                        faces_metric.metric('Faces', f'{len(last_prediction)}')
                else:
                    if frame_count % detection_interval == 0:
                        result_metric.info('👤 Looking for faces...')
                
                # Convert and display
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
                
                time.sleep(0.01)  # Faster frame rate
            
            cap.release()
        else:
            st.info('👆 Click "Start Stream" to begin real-time anti-spoofing detection')

# Footer
st.markdown('---')
st.markdown('''
### 📌 System Status
- ✅ **Tab 1:** MediaPipe Liveness (Blink + Head Movement)
- ✅ **Tab 2:** Anti-Spoofing Detection (Texture + Screen Detection)
- 🎯 **Recommendation:** Use both tabs for maximum security!

**Detection Methods:**
1. **Active (MediaPipe):** Requires user interaction - harder to spoof
2. **Passive (Anti-Spoofing):** Detects static attacks - photos, screens, masks
''')

