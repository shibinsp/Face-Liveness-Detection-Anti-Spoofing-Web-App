import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title='Face Detection with OpenCV', layout='wide')

# Load OpenCV's pre-trained face detector
@st.cache_resource
def load_face_detector():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_face_detector()

st.title('🧠 Face Detection (OpenCV - Simplified Version)')
st.markdown('Upload a photo or use your webcam to detect faces.')
st.info('⚠️ This is a simplified version using OpenCV. For liveness detection, install Visual C++ Build Tools and use app.py')

uploaded_file = st.file_uploader('Upload an image', type=['jpg', 'jpeg', 'png'])
use_webcam = st.checkbox('Use Webcam')

frame = None

if use_webcam:
    st.info('Click Capture Image when ready.')
    cam = st.camera_input('Capture Image')
    if cam is not None:
        file_bytes = np.asarray(bytearray(cam.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)

elif uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

if frame is not None:
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        st.warning('No face detected. Please try again.')
    else:
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(rgb_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(rgb_img, 'Face Detected', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        st.image(rgb_img, channels='RGB', caption=f'Detected {len(faces)} face(s).')
        st.success(f'✅ Detected {len(faces)} face(s)!')
        
        st.markdown('---')
        st.markdown('### To enable liveness detection:')
        st.markdown('1. Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)')
        st.markdown('2. Run `pip install -r requirements.txt`')
        st.markdown('3. Use `streamlit run app.py` instead')

