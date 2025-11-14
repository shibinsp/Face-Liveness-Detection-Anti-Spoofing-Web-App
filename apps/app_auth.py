"""
Face Liveness Detection Authentication System
Complete authentication with registration, login, and face recognition
"""

import streamlit as st
import cv2
import numpy as np
import os
import sys
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import HybridLivenessDetection
from core.database import UserDatabase
from core.face_recognition import FaceRecognitionSystem

# Page configuration
st.set_page_config(
    page_title='Secure Face Authentication System',
    layout='wide',
    page_icon='🔐',
    initial_sidebar_state='collapsed'
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Initialize systems
@st.cache_resource
def init_systems():
    """Initialize all systems"""
    db = UserDatabase()
    face_rec = FaceRecognitionSystem(model_name='Facenet512')
    hybrid_detector = HybridLivenessDetection(
        security_level=3,
        variance_threshold=10,
        edge_threshold=1.0,
        confidence_threshold=0.20
    )
    return db, face_rec, hybrid_detector

db, face_rec, hybrid_detector = init_systems()


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.page = 'login'


def registration_page():
    """Registration page"""
    st.title('🆕 User Registration')
    st.markdown('### Register with Face Recognition')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('#### Enter Your Information')
        
        name = st.text_input('Full Name', key='reg_name', 
                           help='Enter your full name')
        email = st.text_input('Email (Optional)', key='reg_email',
                             help='Enter your email address')
        
        st.markdown('---')
        st.markdown('#### Instructions')
        st.info('''
        1. Enter your name above
        2. Click "Start Camera" to capture your face
        3. Look directly at the camera
        4. Make sure your face is well-lit and clearly visible
        5. Click "Capture & Register" when ready
        ''')
    
    with col2:
        st.markdown('#### Face Capture')
        
        # Camera control
        start_camera = st.checkbox('Start Camera', key='reg_camera')
        
        if start_camera:
            # Create placeholder for video
            video_placeholder = st.empty()
            capture_button_placeholder = st.empty()
            
            # Open camera
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Capture frame
            ret, frame = cap.read()
            
            if ret:
                # Display frame
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect face
                faces = face_rec.detect_faces(frame)
                
                # Draw face boxes
                for (x1, y1, x2, y2) in faces:
                    cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(rgb_frame, 'Face Detected', (x1, y1-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
                
                # Capture button
                if capture_button_placeholder.button('📸 Capture & Register', type='primary', use_container_width=True):
                    if not name:
                        st.error('Please enter your name first!')
                    elif not faces:
                        st.error('No face detected! Please ensure your face is visible.')
                    else:
                        # Process registration
                        with st.spinner('Processing registration...'):
                            # Extract face embedding
                            largest_face = max(faces, key=lambda f: (f[2]-f[0]) * (f[3]-f[1]))
                            embedding = face_rec.extract_face_embedding(frame, largest_face)
                            
                            if embedding is not None:
                                # Save face image
                                image_path = face_rec.save_face_image(frame, name)
                                
                                # Register user
                                success, message = db.register_user(name, embedding, image_path, email)
                                
                                if success:
                                    st.success(f'✅ {message}')
                                    st.balloons()
                                    time.sleep(2)
                                    st.session_state.page = 'login'
                                    st.rerun()
                                else:
                                    st.error(f'❌ {message}')
                            else:
                                st.error('Failed to extract face features. Please try again.')
            
            cap.release()
        else:
            st.info('👆 Check "Start Camera" to begin registration')
    
    st.markdown('---')
    if st.button('← Back to Login'):
        st.session_state.page = 'login'
        st.rerun()


def login_page():
    """Login page with face recognition and liveness detection"""
    st.title('🔐 Secure Face Authentication')
    st.markdown('### Login with Face Recognition + Liveness Detection')
    
    # Check if users exist
    user_count = db.get_user_count()
    
    if user_count == 0:
        st.warning('⚠️ No registered users found. Please register first.')
        if st.button('Go to Registration →', type='primary'):
            st.session_state.page = 'registration'
            st.rerun()
        return
    
    st.info(f'📊 {user_count} registered user(s) in database')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('#### Security Features')
        st.success('✅ **Two-Factor Authentication**')
        st.write('1. **Face Recognition** - Identifies who you are')
        st.write('2. **Liveness Detection** - Verifies you are real')
        st.write('3. **Anti-Spoofing** - Prevents fake photos/videos')
        
        st.markdown('---')
        st.markdown('#### Instructions')
        st.info('''
        1. Click "Start Login Process"
        2. Look directly at the camera
        3. Blink naturally (1-2 times)
        4. Move your head slightly (left/right or up/down)
        5. Wait for verification
        
        ⚡ The system will automatically identify and verify you!
        ''')
        
        # Settings
        with st.expander('⚙️ Advanced Settings'):
            recognition_threshold = st.slider(
                'Recognition Threshold',
                min_value=0.4,
                max_value=0.9,
                value=0.6,
                step=0.05,
                help='Higher = More strict face matching'
            )
            
            security_level = st.select_slider(
                'Security Level',
                options=[1, 2, 3, 4],
                value=3,
                format_func=lambda x: {
                    1: 'Basic', 2: 'Standard', 3: 'High', 4: 'Maximum'
                }[x]
            )
    
    with col2:
        st.markdown('#### Authentication')
        
        start_login = st.button('🎥 Start Login Process', type='primary', use_container_width=True)
        
        if start_login:
            # Create placeholders
            video_placeholder = st.empty()
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            # Open camera
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Get all registered embeddings
            known_embeddings = db.get_all_face_embeddings()
            
            status_placeholder.info('🔄 Initializing authentication...')
            
            # Authentication loop
            frames_processed = 0
            max_frames = 90  # 3 seconds at 30fps
            authenticated = False
            recognized_user_id = None
            recognized_name = None
            
            progress_bar = progress_placeholder.progress(0)
            
            while frames_processed < max_frames and not authenticated:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frames_processed += 1
                progress = min(frames_processed / max_frames, 1.0)
                progress_bar.progress(progress)
                
                # Process every 3rd frame
                if frames_processed % 3 == 0:
                    # Step 1: Face Recognition
                    user_id, name, confidence = face_rec.recognize_face(
                        frame, known_embeddings, threshold=recognition_threshold
                    )
                    
                    if user_id is not None:
                        status_placeholder.success(f'✅ Face Recognized: {name} (Confidence: {confidence:.1%})')
                        recognized_user_id = user_id
                        recognized_name = name
                        
                        # Step 2: Hybrid Liveness Detection
                        result = hybrid_detector.detect_hybrid(frame)
                        
                        # Draw results
                        annotated_frame = hybrid_detector.draw_results(frame, result)
                        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
                        
                        # Check verification
                        if result['verified']:
                            authenticated = True
                            
                            # Update database
                            db.update_last_login(user_id)
                            db.add_login_history(
                                user_id,
                                result['mediapipe_result']['liveness_score'],
                                result['antispoof_result']['confidence'],
                                'success'
                            )
                            
                            # Set session
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_id
                            st.session_state.user_name = name
                            st.session_state.page = 'dashboard'
                            
                            break
                    else:
                        status_placeholder.warning('⚠️ Face not recognized. Please ensure you are registered.')
                        
                        # Still show frame
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(rgb_frame, channels='RGB', use_container_width=True)
                
                time.sleep(0.03)
            
            cap.release()
            progress_bar.empty()
            
            if authenticated:
                status_placeholder.success(f'🎉 Authentication Successful! Welcome {recognized_name}!')
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                status_placeholder.error('❌ Authentication failed. Please try again.')
                if recognized_user_id:
                    db.add_login_history(recognized_user_id, 0, 0, 'failed')
    
    st.markdown('---')
    if st.button('New User? Register Here →'):
        st.session_state.page = 'registration'
        st.rerun()


def dashboard_page():
    """Dashboard/Welcome page after successful login"""
    st.title(f'👋 Welcome, {st.session_state.user_name}!')
    
    # Get user info
    user = db.get_user_by_id(st.session_state.user_id)
    
    # Sidebar
    with st.sidebar:
        st.markdown('### 👤 User Menu')
        
        if user['image_path'] and os.path.exists(user['image_path']):
            st.image(user['image_path'], caption='Your Profile', use_container_width=True)
        
        st.markdown(f"**Name:** {user['name']}")
        if user['email']:
            st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Member Since:** {user['created_at'][:10]}")
        
        st.markdown('---')
        
        if st.button('🚪 Logout', use_container_width=True):
            logout()
            st.rerun()
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('User ID', f'#{user["id"]:04d}')
    
    with col2:
        login_history = db.get_login_history(st.session_state.user_id, limit=10)
        st.metric('Total Logins', len(login_history))
    
    with col3:
        if user['last_login']:
            st.metric('Last Login', user['last_login'][:19])
    
    st.markdown('---')
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(['📊 Dashboard', '📜 Login History', '⚙️ Settings'])
    
    with tab1:
        st.markdown('### Dashboard')
        
        st.success('✅ Authentication Status: **VERIFIED**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Security Features Active')
            st.info('''
            - ✅ Face Recognition
            - ✅ Liveness Detection
            - ✅ Anti-Spoofing Protection
            - ✅ Multi-Factor Verification
            ''')
        
        with col2:
            st.markdown('#### System Information')
            total_users = db.get_user_count()
            st.write(f'**Total Registered Users:** {total_users}')
            st.write(f'**Your User ID:** #{user["id"]:04d}')
            st.write(f'**Account Created:** {user["created_at"][:10]}')
    
    with tab2:
        st.markdown('### Login History')
        
        login_history = db.get_login_history(st.session_state.user_id, limit=20)
        
        if login_history:
            # Create dataframe
            import pandas as pd
            df = pd.DataFrame(login_history)
            
            # Format columns
            df['login_time'] = pd.to_datetime(df['login_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['liveness_score'] = df['liveness_score'].apply(lambda x: f'{x:.2%}' if x > 0 else 'N/A')
            df['confidence_score'] = df['confidence_score'].apply(lambda x: f'{x:.2%}' if x > 0 else 'N/A')
            
            # Display
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            successful_logins = sum(1 for h in login_history if h['status'] == 'success')
            st.metric('Successful Logins', successful_logins)
        else:
            st.info('No login history yet.')
    
    with tab3:
        st.markdown('### Account Settings')
        
        st.warning('🚧 Settings panel coming soon!')
        
        if st.button('🗑️ Delete Account', type='secondary'):
            if st.checkbox('I understand this action cannot be undone'):
                if db.delete_user(st.session_state.user_id):
                    st.success('Account deleted successfully')
                    logout()
                    st.rerun()


# Main app logic
def main():
    """Main application"""
    
    # Route to appropriate page
    if st.session_state.authenticated:
        dashboard_page()
    else:
        if st.session_state.page == 'registration':
            registration_page()
        else:
            login_page()


if __name__ == '__main__':
    main()

