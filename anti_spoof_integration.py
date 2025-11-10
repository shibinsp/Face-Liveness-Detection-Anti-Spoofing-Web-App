"""
Anti-Spoof Package Integration Example

This module demonstrates how to integrate the 'anti-spoof' package
with the existing face liveness detection system.

Installation:
    pip install anti-spoof opencv-python

Usage:
    python anti_spoof_integration.py
"""

import cv2
import streamlit as st
from anti_spoof import AntiSpoof

# Initialize the anti-spoof detector
detector = AntiSpoof()


def detect_with_anti_spoof(image_path_or_frame):
    """
    Detect spoofing using the anti-spoof package
    
    Args:
        image_path_or_frame: Path to image file or numpy array (frame)
        
    Returns:
        dict: Detection results containing is_real, confidence, and attack_type
    """
    # Run detection
    result = detector.detect(image_path_or_frame)
    
    # Extract results
    is_real = result['is_real']
    confidence = result['confidence']
    attack_type = result['attack_type']  # photo, video, mask, etc.
    
    return {
        'is_real': is_real,
        'confidence': confidence,
        'attack_type': attack_type,
        'label': 'Real' if is_real else f'Fake ({attack_type})'
    }


def detect_from_webcam():
    """Real-time detection from webcam using anti-spoof"""
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect with anti-spoof
        result = detect_with_anti_spoof(frame)
        
        # Display results
        color = (0, 255, 0) if result['is_real'] else (0, 0, 255)
        label = f"{result['label']} - {result['confidence']:.2f}"
        
        cv2.putText(frame, label, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Show frame
        cv2.imshow('Anti-Spoof Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def detect_from_image(image_path):
    """Detect from image file"""
    result = detect_with_anti_spoof(image_path)
    
    print(f"Is Real: {result['is_real']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Attack Type: {result['attack_type']}")
    
    return result


# Streamlit integration
def streamlit_app():
    """
    Streamlit app using anti-spoof package
    """
    st.title("🛡️ Anti-Spoof Detection")
    st.markdown("*Powered by anti-spoof package*")
    
    # Upload option
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Read image
        file_bytes = uploaded_file.read()
        nparr = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        # Display image
        st.image(cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB), caption='Uploaded Image')
        
        # Detect
        with st.spinner('Analyzing...'):
            result = detect_with_anti_spoof(nparr)
        
        # Show results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if result['is_real']:
                st.success(f"✅ Real Person")
            else:
                st.error(f"❌ Fake Detected")
        
        with col2:
            st.metric("Confidence", f"{result['confidence']:.1%}")
        
        with col3:
            st.info(f"Type: {result['attack_type']}")
    
    # Webcam option
    st.markdown("---")
    if st.button("Start Webcam Detection"):
        st.info("Opening webcam... Press 'q' in the OpenCV window to quit")
        detect_from_webcam()


# Combined detection with existing system
def combined_detection(frame):
    """
    Combine anti-spoof package with existing detection methods
    
    Returns both results for comparison
    """
    from anti_spoofing import TextureAntiSpoofing, FaceDetector
    
    # Method 1: anti-spoof package
    result_package = detect_with_anti_spoof(frame)
    
    # Method 2: Our custom anti-spoofing
    face_detector = FaceDetector()
    texture_detector = TextureAntiSpoofing()
    
    faces = face_detector.detect(frame)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        bbox = (x, y, x+w, y+h)
        is_real, confidence, label, scores = texture_detector.predict(frame, bbox)
        
        result_custom = {
            'is_real': is_real,
            'confidence': confidence,
            'label': label,
            'scores': scores
        }
    else:
        result_custom = {
            'is_real': False,
            'confidence': 0.0,
            'label': 'No Face',
            'scores': {}
        }
    
    return {
        'anti_spoof_package': result_package,
        'custom_detection': result_custom
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Image mode
        image_path = sys.argv[1]
        print(f"Analyzing image: {image_path}")
        detect_from_image(image_path)
    else:
        # Webcam mode
        print("Starting webcam detection...")
        detect_from_webcam()

