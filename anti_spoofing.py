"""
Anti-Spoofing Detection Module
Supports both ONNX model-based and texture-based detection
"""

import cv2
import numpy as np
import os

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


class AntiSpoofing:
    """ONNX model-based anti-spoofing detector"""
    
    def __init__(self, model_path):
        """
        Initialize anti-spoofing detector with ONNX model
        
        Args:
            model_path: path to .onnx model file
        """
        if not ONNX_AVAILABLE:
            raise ImportError("onnxruntime not installed. Run: pip install onnxruntime")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = (80, 80)  # Model input size
        
    def preprocess(self, image, bbox):
        """
        Preprocess face image for model
        
        Args:
            image: Original image
            bbox: Face bounding box (x1, y1, x2, y2)
            
        Returns:
            Preprocessed face tensor
        """
        # Extract face region
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are within image bounds
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        face = image[y1:y2, x1:x2]
        
        if face.size == 0:
            return None
        
        # Resize to model input size
        face = cv2.resize(face, self.input_shape)
        
        # Normalize
        face = face.astype(np.float32) / 255.0
        face = (face - 0.5) / 0.5
        
        # Add batch dimension
        face = np.transpose(face, (2, 0, 1))
        face = np.expand_dims(face, axis=0)
        
        return face
    
    def predict(self, image, bbox):
        """
        Predict if face is real or fake
        
        Args:
            image: Original image
            bbox: Face bounding box (x1, y1, x2, y2)
            
        Returns:
            (is_real, confidence, label)
        """
        # Preprocess
        input_data = self.preprocess(image, bbox)
        
        if input_data is None:
            return False, 0.0, "Invalid"
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: input_data})
        score = outputs[0][0][1]  # Real face score
        
        # Classify
        is_real = score > 0.5
        label = "Real" if is_real else "Fake"
        confidence = score if is_real else (1 - score)
        
        return is_real, confidence, label


class TextureAntiSpoofing:
    """Texture-based anti-spoofing (no model required)"""
    
    def __init__(self, variance_threshold=100, edge_threshold=50, confidence_threshold=0.45):
        """
        Initialize texture-based anti-spoofing
        
        Args:
            variance_threshold: Laplacian variance threshold
            edge_threshold: Edge density threshold
            confidence_threshold: Threshold for classifying as real (0.0-1.0)
        """
        self.variance_threshold = variance_threshold
        self.edge_threshold = edge_threshold
        self.confidence_threshold = confidence_threshold
    
    def calculate_texture_score(self, face_img):
        """
        Calculate texture richness score
        Real faces have more texture variation than printed photos
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Texture score (higher = more likely real)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Calculate Local Binary Pattern variance
        # Photos have lower variance
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return variance
    
    def calculate_edge_density(self, face_img):
        """
        Calculate edge density
        Real faces have more natural edges than printed photos
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Edge density score
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate edge density
        edge_density = np.sum(edges > 0) / edges.size * 100
        
        return edge_density
    
    def calculate_color_diversity(self, face_img):
        """
        Calculate color diversity
        Real faces have more color variation than printed photos
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Color diversity score
        """
        # Convert to HSV
        hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
        
        # Calculate standard deviation of hue and saturation
        hue_std = np.std(hsv[:, :, 0])
        sat_std = np.std(hsv[:, :, 1])
        
        # Combined score
        color_diversity = (hue_std + sat_std) / 2
        
        return color_diversity
    
    def detect_moire_pattern(self, face_img):
        """
        Detect moiré patterns which are common in screen displays
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Moiré pattern score (higher = more likely from screen)
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Resize for consistent processing
        gray = cv2.resize(gray, (128, 128))
        
        # Apply FFT to detect periodic patterns
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.abs(fshift)
        
        # Calculate the ratio of high frequency energy to detect periodic patterns
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Define high frequency region (outer areas)
        # Screens show regular patterns in specific frequency bands
        mask = np.zeros((h, w))
        cv2.circle(mask, (center_w, center_h), 20, 1, -1)  # Low freq (center)
        cv2.circle(mask, (center_w, center_h), 10, 0, -1)   # Remove DC component
        
        # High frequency energy (excluding center)
        high_freq_energy = np.sum(magnitude_spectrum * (1 - mask))
        low_freq_energy = np.sum(magnitude_spectrum * mask)
        
        # Ratio indicates periodicity (screens have higher ratio)
        if low_freq_energy > 0:
            ratio = (high_freq_energy / low_freq_energy) * 1000  # Scale for readability
        else:
            ratio = 0
        
        # Clamp to reasonable range
        return min(ratio, 100)
    
    def detect_screen_reflection(self, face_img):
        """
        Detect specular reflections common in screens
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Reflection score (higher = more likely screen)
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Detect very bright spots (specular reflections)
        _, bright_spots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of very bright pixels
        bright_ratio = np.sum(bright_spots > 0) / bright_spots.size * 100
        
        return bright_ratio
    
    def calculate_noise_pattern(self, face_img):
        """
        Analyze noise patterns - real faces have natural noise, screens have different noise
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Noise score
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur and subtract to get noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = cv2.absdiff(gray, blurred)
        
        # Real faces have more natural, random noise
        # Screens have more uniform or compressed noise
        noise_std = np.std(noise)
        
        return noise_std
    
    def detect_pixel_grid(self, face_img):
        """
        Detect regular pixel grid patterns from screens
        
        Args:
            face_img: Face image (BGR)
            
        Returns:
            Grid pattern score (higher = more likely screen)
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Resize to make pixel grid more visible if present
        small = cv2.resize(gray, (gray.shape[1] // 2, gray.shape[0] // 2))
        resized_back = cv2.resize(small, (gray.shape[1], gray.shape[0]))
        
        # Calculate difference - screens show more regular patterns
        diff = cv2.absdiff(gray, resized_back)
        grid_score = np.mean(diff)
        
        return grid_score
    
    def detect_color_saturation(self, face_img):
        """Analyze color saturation - phone screens often have unnatural saturation"""
        hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        mean_sat = np.mean(saturation)
        std_sat = np.std(saturation)
        
        anomaly_score = 0
        if mean_sat < 30 or mean_sat > 120:
            anomaly_score += 30
        if std_sat < 15:  # Too uniform
            anomaly_score += 20
        return anomaly_score
    
    def detect_depth_gradient(self, face_img):
        """Detect flatness - real faces have 3D depth, screens are flat"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        grad_std = np.std(gradient_magnitude)
        
        if grad_std < 15:
            return 40
        elif grad_std < 25:
            return 20
        return 0
    
    def detect_rectangular_boundary(self, face_img):
        """Detect sharp rectangular boundaries (phone screen bezel)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            h_lines = v_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 10 or angle > 170:
                    h_lines += 1
                elif 80 < angle < 100:
                    v_lines += 1
            
            if h_lines > 2 and v_lines > 2:
                return 50
            elif h_lines > 1 or v_lines > 1:
                return 25
        return 0
    
    def detect_lighting_uniformity(self, face_img):
        """Analyze lighting - phone screens have artificial uniform backlight"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        grid_size = 4
        cell_h, cell_w = h // grid_size, w // grid_size
        
        cell_means = []
        for i in range(grid_size):
            for j in range(grid_size):
                cell = gray[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                cell_means.append(np.mean(cell))
        
        brightness_variation = np.std(cell_means)
        if brightness_variation < 10:
            return 40
        elif brightness_variation < 20:
            return 20
        return 0
    
    def predict(self, image, bbox):
        """
        Predict if face is real or fake using texture analysis
        
        Args:
            image: Original image (BGR)
            bbox: Face bounding box (x1, y1, x2, y2)
            
        Returns:
            (is_real, confidence, label, details)
        """
        # Extract face region
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are within image bounds
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        face = image[y1:y2, x1:x2]
        
        if face.size == 0:
            return False, 0.0, "Invalid", {}
        
        # Calculate multiple features
        texture_score = self.calculate_texture_score(face)
        edge_density = self.calculate_edge_density(face)
        color_diversity = self.calculate_color_diversity(face)
        
        # NEW: Enhanced anti-spoofing features for screen detection
        moire_score = self.detect_moire_pattern(face)
        reflection_score = self.detect_screen_reflection(face)
        noise_score = self.calculate_noise_pattern(face)
        grid_score = self.detect_pixel_grid(face)
        
        # PHONE SCREEN SPECIFIC DETECTION
        saturation_anomaly = self.detect_color_saturation(face)
        depth_score = self.detect_depth_gradient(face)
        boundary_score = self.detect_rectangular_boundary(face)
        lighting_uniformity = self.detect_lighting_uniformity(face)
        
        scores = {
            'texture': texture_score,
            'edges': edge_density,
            'color': color_diversity,
            'moire': moire_score,
            'reflection': reflection_score,
            'noise': noise_score,
            'grid': grid_score,
            'saturation': saturation_anomaly,
            'depth': depth_score,
            'boundary': boundary_score,
            'lighting': lighting_uniformity
        }
        
        # Improved scoring algorithm with screen detection
        # Real faces typically have:
        # - Texture variance: 100-500 (very important)
        # - Edge density: 5-15% (moderate importance)
        # - Color diversity: 15-50 (less important)
        # - Low moiré patterns (< 30)
        # - Low specular reflections (< 5%)
        # - Natural noise (3-15)
        # - Low grid patterns (< 15)
        
        # Normalize basic scores - EXTREMELY LENIENT for real faces
        # Real faces: Give high base scores even for low-quality webcams
        texture_norm = min(max(texture_score - 10, 0) / 100, 1.0)  # Very lenient
        edge_norm = min(max(edge_density - 1, 0) / 8, 1.0)  # Very lenient
        color_norm = min(max(color_diversity - 3, 0) / 25, 1.0)  # Very lenient
        
        # Normalize screen detection scores (inverted - higher values mean more likely fake)
        moire_penalty = min(max(moire_score - 40, 0) / 40, 1.0)  # Only penalize very high moiré
        reflection_penalty = min(max(reflection_score - 8, 0) / 10, 1.0)  # Only penalize very bright
        noise_bonus = min(max(noise_score - 1, 0) / 20, 1.0)  # Bonus for any noise
        grid_penalty = min(max(grid_score - 20, 0) / 20, 1.0)  # Only penalize strong grids
        
        # NEW: Phone screen detection penalties
        saturation_penalty = min(saturation_anomaly / 50, 1.0)  # Unnatural color saturation
        depth_penalty = min(depth_score / 40, 1.0)  # Flat image (no 3D depth)
        boundary_penalty = min(boundary_score / 50, 1.0)  # Rectangular screen bezel
        lighting_penalty = min(lighting_uniformity / 40, 1.0)  # Artificial uniform backlight
        
        # Base confidence from traditional features - VERY HIGH BASE for real faces
        # Give generous starting point to real faces
        base_confidence = (texture_norm * 0.50 + edge_norm * 0.30 + color_norm * 0.20)
        
        # Add baseline bonus for any detected face
        base_confidence = min(base_confidence + 0.15, 1.0)  # 15% bonus just for being a face
        
        # Apply ALL screen detection penalties - INCREASED IMPACT
        screen_penalty = (
            moire_penalty * 0.10 + 
            reflection_penalty * 0.08 + 
            grid_penalty * 0.05 +
            saturation_penalty * 0.12 +  # NEW
            depth_penalty * 0.15 +  # NEW - Most important for phone screens
            boundary_penalty * 0.15 +  # NEW - Detects phone bezel
            lighting_penalty * 0.12   # NEW - Uniform backlight
        )
        
        # Final confidence with noise bonus
        confidence = base_confidence + (noise_bonus * 0.08) - screen_penalty
        confidence = max(0.0, min(confidence, 1.0))  # Clamp to [0, 1]
        
        # CRITICAL: Phone screen killer rules - BALANCED APPROACH
        # Detect phone screens while allowing real faces
        phone_screen_indicators = 0
        
        # BALANCED phone detection - Use tiered thresholds
        phone_screen_indicators = 0
        strong_phone_signals = 0  # Track strong evidence
        
        # Strong evidence thresholds (clear phone characteristics)
        if depth_score > 30:  # Very flat
            phone_screen_indicators += 1
            strong_phone_signals += 1
        elif depth_score > 18:  # Somewhat flat
            phone_screen_indicators += 1
            
        if boundary_score > 35:  # Clear bezel
            phone_screen_indicators += 1
            strong_phone_signals += 1
        elif boundary_score > 22:
            phone_screen_indicators += 1
            
        if lighting_uniformity > 30:  # Very uniform
            phone_screen_indicators += 1
            strong_phone_signals += 1
        elif lighting_uniformity > 18:
            phone_screen_indicators += 1
            
        if moire_score > 35:  # Strong pattern
            phone_screen_indicators += 1
            strong_phone_signals += 1
        elif moire_score > 22:
            phone_screen_indicators += 1
        
        # Weaker supporting evidence
        if reflection_score > 8:
            phone_screen_indicators += 1
        if saturation_anomaly > 35:
            phone_screen_indicators += 1
        if texture_score > 250:
            phone_screen_indicators += 1
        
        # Apply penalties based on evidence strength
        if strong_phone_signals >= 2:  # 2+ strong signals = definitely phone
            confidence = confidence * 0.25  # 75% penalty
        elif phone_screen_indicators >= 4:  # 4+ total signals = likely phone
            confidence = confidence * 0.40  # 60% penalty
        elif phone_screen_indicators >= 3:  # 3 signals = possible phone
            confidence = confidence * 0.60  # 40% penalty
        elif phone_screen_indicators >= 2:  # 2 signals = weak evidence
            confidence = confidence * 0.80  # 20% penalty
        
        # Additional rules for clear cases
        # MASSIVE BOOST for real faces - assume real unless proven fake
        if phone_screen_indicators == 0:
            # If no phone indicators, assume it's real and boost heavily
            if texture_score > 30:  # Very low threshold
                confidence = min(confidence * 1.50, 1.0)  # Huge boost
            elif texture_score > 20:
                confidence = min(confidence * 1.35, 1.0)
            else:
                confidence = min(confidence * 1.20, 1.0)  # Boost even very low texture
        
        # Strong penalty ONLY for very obvious screen indicators
        if reflection_score > 15 or moire_score > 60:
            confidence = confidence * 0.70
        
        # Penalize ONLY extremely uniform faces (very obvious screens)
        if texture_score < 30 and noise_score < 1:
            confidence = confidence * 0.60
        
        # Classify using custom threshold
        is_real = confidence > self.confidence_threshold
        label = "Real" if is_real else "Fake"
        
        return is_real, confidence, label, scores


class FaceDetector:
    """Simple face detector using Haar Cascades"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # Load eye cascade for additional validation
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def is_valid_face(self, x, y, w, h, gray_image):
        """
        Validate if detected region is actually a face
        
        Args:
            x, y, w, h: Bounding box coordinates
            gray_image: Grayscale image
            
        Returns:
            Boolean indicating if it's a valid face
        """
        # Check aspect ratio (faces are roughly rectangular, not too wide or tall)
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            return False
        
        # Check minimum size (avoid tiny detections)
        if w < 60 or h < 60:
            return False
        
        # Try to detect eyes within the face region (optional but helpful)
        face_roi = gray_image[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
        
        # If we detect at least one eye, it's more likely a real face
        # But we don't make it mandatory to avoid false negatives
        has_eyes = len(eyes) > 0
        
        return True  # Basic checks passed
    
    def detect(self, image):
        """
        Detect faces and return bounding boxes
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # More strict parameters to reduce false positives
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=7,      # Increased from 5 to reduce false positives
            minSize=(80, 80),    # Increased from (30, 30) to filter small detections
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Filter faces using validation
        valid_faces = []
        for (x, y, w, h) in faces:
            if self.is_valid_face(x, y, w, h, gray):
                valid_faces.append((x, y, w, h))
        
        return np.array(valid_faces) if valid_faces else np.array([])


def download_models_info():
    """
    Information about downloading Silent-Face-Anti-Spoofing models
    
    Returns:
        Dictionary with download instructions
    """
    return {
        "repository": "https://github.com/minivision-ai/Silent-Face-Anti-Spoofing",
        "models": [
            "2.7_80x80_MiniFASNetV2.onnx",
            "4_0_0_80x80_MiniFASNetV1SE.onnx"
        ],
        "instructions": """
        1. Clone repository:
           git clone https://github.com/minivision-ai/Silent-Face-Anti-Spoofing.git
           
        2. Download models:
           cd Silent-Face-Anti-Spoofing
           # Follow repository instructions to download pre-trained models
           
        3. Copy model files to your project:
           Copy .onnx files to: models/ directory
        
        4. Model capabilities:
           - Real face detection
           - Printed photo detection
           - Video replay detection
           - Mask detection
        """
    }


if __name__ == "__main__":
    # Test texture-based anti-spoofing
    print("Testing Texture-Based Anti-Spoofing...")
    
    # Initialize
    detector = FaceDetector()
    anti_spoof = TextureAntiSpoofing()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        faces = detector.detect(frame)
        
        for (x, y, w, h) in faces:
            bbox = (x, y, x+w, y+h)
            
            # Check if real or fake
            is_real, confidence, label, scores = anti_spoof.predict(frame, bbox)
            
            # Draw results
            color = (0, 255, 0) if is_real else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            text = f"{label}: {confidence:.2f}"
            cv2.putText(frame, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Display scores
            score_text = f"T:{scores['texture']:.0f} E:{scores['edges']:.1f}"
            cv2.putText(frame, score_text, (x, y+h+20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        cv2.imshow('Anti-Spoofing Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

