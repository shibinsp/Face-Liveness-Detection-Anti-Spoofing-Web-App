"""
Hybrid Face Liveness Detection System
Combines MediaPipe (active) + Anti-spoofing (passive) for maximum security
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import HybridLivenessDetection

st.set_page_config(
    page_title='Hybrid Face Liveness Detection',
    layout='wide',
    page_icon='🔐'
)

# Initialize session state
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'verification_log' not in st.session_state:
    st.session_state.verification_log = []
if 'hybrid_detector' not in st.session_state:
    st.session_state.hybrid_detector = None

# Title
st.title('🔐 Hybrid Face Liveness Detection System')
st.markdown('**Two-Factor Verification:** MediaPipe Liveness + Anti-Spoofing Detection')

# Sidebar configuration
with st.sidebar:
    st.markdown('## ⚙️ Security Settings')
    
    security_level = st.select_slider(
        '🔒 Security Level',
        options=[1, 2, 3, 4],
        value=3,
        format_func=lambda x: {
            1: '🔓 Basic (Anti-spoofing only)',
            2: '🔐 Standard (Either passes)',
            3: '🔒 High (Both must pass)',
            4: '🔐 Maximum (Both + Challenges)'
        }[x],
        help='Higher levels = More secure but stricter'
    )
    
    st.markdown('---')
    st.markdown('### 🛡️ Anti-Spoofing Settings')
    
    detection_quality = st.select_slider(
        'Detection Sensitivity',
        options=['Very Lenient', 'Lenient', 'Balanced', 'Strict'],
        value='Very Lenient',
        help='Adjust for your lighting conditions'
    )
    
    quality_map = {
        'Very Lenient': (10, 1.0, 0.20),  # Extremely lenient - assume real unless proven fake
        'Lenient': (30, 1.5, 0.25),
        'Balanced': (50, 2.5, 0.30),
        'Strict': (70, 3.5, 0.35)
    }
    variance_threshold, edge_threshold, confidence_threshold = quality_map[detection_quality]
    
    st.info(f'**{detection_quality}**\n- Texture: {variance_threshold}\n- Edge: {edge_threshold}\n- Threshold: {confidence_threshold}')
    
    st.markdown('---')
    st.markdown('### 📊 System Status')
    
    level_descriptions = {
        1: '**Basic:** Only checks if image is from a screen',
        2: '**Standard:** Checks liveness OR screen detection',
        3: '**High:** Requires BOTH liveness AND no screen',
        4: '**Maximum:** Requires liveness + no screen + challenges'
    }
    st.success(level_descriptions[security_level])
    
    if security_level == 4:
        st.warning('**Challenges Required:**\n- 👁️ Blink 2+ times\n- 🔄 Move head in 2+ directions\n- 🛡️ Pass anti-spoofing')

# Initialize detector with current settings
@st.cache_resource
def get_detector(_security_level, _var_thresh, _edge_thresh, _conf_thresh):
    """Create detector (use _ prefix to avoid hashing issues)"""
    return HybridLivenessDetection(
        security_level=_security_level,
        variance_threshold=_var_thresh,
        edge_threshold=_edge_thresh,
        confidence_threshold=_conf_thresh
    )

# Recreate detector if settings changed
detector_key = f"{security_level}_{variance_threshold}_{edge_threshold}_{confidence_threshold}"
if st.session_state.hybrid_detector is None or getattr(st.session_state, 'detector_key', None) != detector_key:
    st.session_state.hybrid_detector = HybridLivenessDetection(
        security_level=security_level,
        variance_threshold=variance_threshold,
        edge_threshold=edge_threshold,
        confidence_threshold=confidence_threshold
    )
    st.session_state.detector_key = detector_key

hybrid_detector = st.session_state.hybrid_detector

# Main content
st.markdown('---')

# Detection mode
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('### 📷 Detection Mode')
    detection_mode = st.radio(
        'Select Mode',
        ['Single Image', 'Live Webcam'],
        horizontal=True
    )

with col2:
    st.markdown('### 📈 Statistics')
    stats = hybrid_detector.get_statistics()
    if stats['total_attempts'] > 0:
        st.metric('Success Rate', f"{stats['success_rate']:.1%}")
        st.metric('Verified', f"{stats['verified_count']}/{stats['total_attempts']}")
    else:
        st.info('No verification attempts yet')

st.markdown('---')

# Single Image Mode
if detection_mode == 'Single Image':
    st.session_state.webcam_running = False
    
    st.markdown('### 📸 Upload or Capture Image')
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            'Upload Image',
            type=['jpg', 'jpeg', 'png'],
            help='Upload a photo to verify'
        )
    
    with col2:
        use_camera = st.checkbox('Use Camera Instead')
        if use_camera:
            camera_input = st.camera_input('Capture Photo')
    
    # Process image
    frame = None
    if use_camera and 'camera_input' in locals() and camera_input:
        file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
    elif uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
    
    if frame is not None:
        with st.spinner('🔍 Analyzing...'):
            # Perform hybrid detection
            result = hybrid_detector.detect_hybrid(frame)
            annotated_frame = hybrid_detector.draw_results(frame, result)
            
            # Display result
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            st.image(rgb_frame, use_container_width=True)
            
            # Result details
            st.markdown('---')
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if result['verified']:
                    st.success(f'### ✅ VERIFIED')
                    st.success(f"**{result['verification_level']}** Security")
                else:
                    st.error(f'### ❌ NOT VERIFIED')
                    st.error(f"**{result['verification_level']}** Security")
            
            with col2:
                st.metric('Combined Confidence', f"{result['combined_confidence']:.1%}")
                st.metric('Security Level', result['verification_level'])
            
            with col3:
                mp_result = result['mediapipe_result']
                as_result = result['antispoof_result']
                
                if mp_result['is_live']:
                    st.success(f'👁️ MediaPipe: LIVE')
                else:
                    st.error(f'👁️ MediaPipe: NOT LIVE')
                
                if as_result['is_real']:
                    st.success(f'🛡️ Anti-spoof: REAL')
                else:
                    st.error(f'🛡️ Anti-spoof: FAKE')
            
            # Detailed breakdown
            with st.expander('📊 Detailed Analysis'):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown('**MediaPipe Results:**')
                    st.write(f"- Face detected: {mp_result['has_face']}")
                    st.write(f"- Blink count: {mp_result['blink_count']}")
                    st.write(f"- Head movements: {len(mp_result['head_movements'])}")
                    st.write(f"- Liveness score: {mp_result['liveness_score']:.1%}")
                
                with col_b:
                    st.markdown('**Anti-spoofing Results:**')
                    st.write(f"- Classification: {as_result['label']}")
                    st.write(f"- Confidence: {as_result['confidence']:.1%}")
                    st.write(f"- Phone indicators: {as_result['phone_indicators']}/4")
                    
                    if as_result['likely_phone']:
                        st.error('⚠️ **PHONE SCREEN DETECTED!**')
                
                # Detailed scores
                if as_result['scores']:
                    st.markdown('**Detailed Scores:**')
                    scores_df = pd.DataFrame([as_result['scores']])
                    st.dataframe(scores_df, use_container_width=True)
            
            # Message
            st.info(result['message'])
            
            # Log
            st.session_state.verification_log.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': 'Single Image',
                'verified': result['verified'],
                'confidence': result['combined_confidence'],
                'level': result['verification_level']
            })

# Live Webcam Mode
else:
    st.markdown('### 📹 Live Webcam Verification')
    
    # Control buttons
    button_col1, button_col2, button_col3 = st.columns([1, 1, 3])
    
    with button_col1:
        if st.button('🎥 Start Verification', disabled=st.session_state.webcam_running, use_container_width=True):
            st.session_state.webcam_running = True
            st.rerun()
    
    with button_col2:
        if st.button('⏹️ Stop', disabled=not st.session_state.webcam_running, type='primary', use_container_width=True):
            st.session_state.webcam_running = False
            st.rerun()
    
    st.markdown('---')
    
    if st.session_state.webcam_running:
        st.success('🔴 LIVE VERIFICATION IN PROGRESS')
        
        # Placeholders
        video_placeholder = st.empty()
        status_placeholder = st.empty()
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        # Metrics placeholders
        verification_metric = metrics_col1.empty()
        confidence_metric = metrics_col2.empty()
        mediapipe_metric = metrics_col3.empty()
        antispoof_metric = metrics_col4.empty()
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        detection_interval = 2  # Process every 2nd frame
        last_result = None
        
        while st.session_state.webcam_running:
            ret, frame = cap.read()
            if not ret:
                st.error('Failed to access camera')
                break
            
            frame_count += 1
            
            # Process every Nth frame
            if frame_count % detection_interval == 0:
                result = hybrid_detector.detect_hybrid(frame)
                last_result = result
            
            # Draw results using last result
            if last_result:
                annotated_frame = hybrid_detector.draw_results(frame, last_result)
                
                # Update metrics
                if last_result['verified']:
                    verification_metric.success('✅ VERIFIED')
                else:
                    verification_metric.error('❌ NOT VERIFIED')
                
                confidence_metric.metric('Confidence', f"{last_result['combined_confidence']:.1%}")
                
                mp_result = last_result['mediapipe_result']
                as_result = last_result['antispoof_result']
                
                if mp_result['is_live']:
                    mediapipe_metric.success(f'👁️ LIVE\n{mp_result["liveness_score"]:.0%}')
                else:
                    mediapipe_metric.warning(f'👁️ Waiting\n{mp_result["liveness_score"]:.0%}')
                
                if as_result['is_real']:
                    antispoof_metric.success(f'🛡️ REAL\n{as_result["confidence"]:.0%}')
                else:
                    antispoof_metric.error(f'🛡️ FAKE\n{as_result["confidence"]:.0%}')
                
                # Status message
                status_placeholder.info(last_result['message'])
            else:
                annotated_frame = frame
            
            # Display frame
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
            
            time.sleep(0.03)  # ~30 FPS
        
        cap.release()
    else:
        st.info('👆 Click "Start Verification" to begin live detection')
        
        # Show instructions
        st.markdown('### 📋 Instructions')
        
        if security_level == 1:
            st.write('**Basic Mode:**')
            st.write('- System will check if the image is from a screen or photo')
            st.write('- No liveness check required')
        elif security_level == 2:
            st.write('**Standard Mode:**')
            st.write('- Either blink/move OR pass anti-spoofing')
            st.write('- Good for quick verification')
        elif security_level == 3:
            st.write('**High Security Mode:**')
            st.write('1. 👁️ Blink or move your head (liveness)')
            st.write('2. 🛡️ Must not be a phone screen/photo')
            st.write('3. ✅ Both must pass to verify')
        elif security_level == 4:
            st.write('**Maximum Security Mode:**')
            st.write('1. 👁️ Blink at least 2 times')
            st.write('2. 🔄 Move head in 2+ directions')
            st.write('3. 🛡️ Must not be a phone screen/photo')
            st.write('4. ✅ All challenges must be completed')

# Show logs
if st.session_state.verification_log:
    st.markdown('---')
    with st.expander('📋 Verification Log'):
        df = pd.DataFrame(st.session_state.verification_log)
        st.dataframe(df, use_container_width=True)
        
        if st.button('Clear Log'):
            st.session_state.verification_log = []
            st.rerun()

# Footer
st.markdown('---')
st.markdown('''
### 🔐 Security Levels Explained

| Level | Name | Requirements | Best For |
|-------|------|--------------|----------|
| 1 | 🔓 Basic | Anti-spoofing only | Quick checks |
| 2 | 🔐 Standard | Liveness OR Anti-spoofing | General use |
| 3 | 🔒 High | Liveness AND Anti-spoofing | **Recommended** |
| 4 | 🔐 Maximum | Both + Challenges (2+ blinks, 2+ movements) | Maximum security |

**How it works:**
- **MediaPipe:** Detects if you're a live person (blinks, head movement)
- **Anti-spoofing:** Detects if image is from a phone screen, photo, or video
- **Combined:** Both must pass = Maximum confidence it's really you!
''')

