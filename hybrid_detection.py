"""
Hybrid Face Liveness Detection System
Combines MediaPipe (active liveness) + Anti-spoofing (passive screen detection)

This provides TWO-FACTOR authentication:
1. MediaPipe: Verifies the person is LIVE (blinks, head movement)
2. Anti-spoofing: Verifies it's NOT a screen/photo/video replay

Both must pass for verification!
"""

import cv2
import numpy as np
import time
from mediapipe_liveness import MediaPipeLiveness
from anti_spoofing import TextureAntiSpoofing, FaceDetector


class HybridLivenessDetection:
    """
    Hybrid detection combining MediaPipe and Anti-spoofing
    
    Verification Levels:
    - Level 1 (Basic): Anti-spoofing only (passive)
    - Level 2 (Standard): MediaPipe OR Anti-spoofing (one must pass)
    - Level 3 (High): MediaPipe AND Anti-spoofing (both must pass)
    - Level 4 (Maximum): MediaPipe + Anti-spoofing + Challenge mode
    """
    
    def __init__(self, security_level=3, variance_threshold=50, edge_threshold=2.5, confidence_threshold=0.35):
        """
        Initialize hybrid detection system
        
        Args:
            security_level: 1-4 (1=Basic, 2=Standard, 3=High, 4=Maximum)
            variance_threshold: Texture variance threshold for anti-spoofing
            edge_threshold: Edge density threshold for anti-spoofing
            confidence_threshold: Confidence threshold for anti-spoofing
        """
        self.security_level = security_level
        
        # Initialize both detection systems
        self.mediapipe_detector = MediaPipeLiveness()
        self.face_detector = FaceDetector()
        self.anti_spoof = TextureAntiSpoofing(variance_threshold, edge_threshold, confidence_threshold)
        
        # State tracking
        self.last_mediapipe_result = None
        self.last_antispoof_result = None
        self.verification_history = []
        
    def detect_hybrid(self, frame):
        """
        Perform hybrid detection on a frame
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            {
                'verified': bool,
                'verification_level': str,
                'mediapipe_result': dict,
                'antispoof_result': dict,
                'combined_confidence': float,
                'message': str
            }
        """
        result = {
            'verified': False,
            'verification_level': 'UNKNOWN',
            'mediapipe_result': None,
            'antispoof_result': None,
            'combined_confidence': 0.0,
            'message': '',
            'details': []
        }
        
        # Step 1: MediaPipe Liveness Detection
        mp_processed_frame, blink_info, head_pose_info, is_live = self.mediapipe_detector.process_frame(frame)
        
        # Extract head movements
        if head_pose_info:
            movements_dict = head_pose_info['movements_detected']
            head_movements = [k for k, v in movements_dict.items() if v and k != 'neutral']
            blink_count = blink_info['total_blinks']
            has_face = True
        else:
            head_movements = []
            blink_count = 0
            has_face = False
        
        # Calculate liveness score
        # Base score from face detection
        liveness_score = 0.0
        if has_face:
            liveness_score = 0.3  # Base score for having a face
            
            # Add points for blinks (up to 0.4)
            if blink_count > 0:
                liveness_score += min(blink_count * 0.2, 0.4)
            
            # Add points for head movements (up to 0.3)
            if len(head_movements) > 0:
                liveness_score += min(len(head_movements) * 0.15, 0.3)
        
        liveness_score = min(liveness_score, 1.0)
        
        mediapipe_result = {
            'has_face': has_face,
            'blink_count': blink_count,
            'head_movements': head_movements,
            'liveness_score': liveness_score,
            'is_live': liveness_score > 0.5
        }
        
        # Step 2: Anti-spoofing Detection - PROCESS ALL FACES
        faces = self.face_detector.detect(frame)
        
        all_face_results = []
        
        if len(faces) > 0:
            # Process EACH face independently
            for (x, y, w, h) in faces:
                bbox = (x, y, x+w, y+h)
                
                is_real, confidence, label, scores = self.anti_spoof.predict(frame, bbox)
                
                # AGGRESSIVE phone screen detection - LOWER THRESHOLDS
                phone_indicators = 0
                phone_reasons = []
                
                # Get scores
                depth = scores.get('depth', 0)
                boundary = scores.get('boundary', 0)
                lighting = scores.get('lighting', 0)
                saturation = scores.get('saturation', 0)
                moire = scores.get('moire', 0)
                reflection = scores.get('reflection', 0)
                texture = scores.get('texture', 0)
                edges = scores.get('edges', 0)
                
                # SMART phone detection - Use COMBINATION logic, not just thresholds
                phone_indicators = 0
                phone_reasons = []
                
                # STRONG indicators (high confidence it's a phone)
                strong_indicators = 0
                
                # Check critical phone characteristics
                if depth > 30:  # Very flat = strong phone indicator
                    phone_indicators += 1
                    strong_indicators += 1
                    phone_reasons.append(f'FLAT:{depth:.0f}')
                elif depth > 18:  # Somewhat flat
                    phone_indicators += 1
                    phone_reasons.append(f'flat:{depth:.0f}')
                    
                if boundary > 35:  # Clear bezel = strong indicator
                    phone_indicators += 1
                    strong_indicators += 1
                    phone_reasons.append(f'BEZEL:{boundary:.0f}')
                elif boundary > 22:
                    phone_indicators += 1
                    phone_reasons.append(f'bezel:{boundary:.0f}')
                
                if lighting > 30:  # Very uniform = strong indicator
                    phone_indicators += 1
                    strong_indicators += 1
                    phone_reasons.append(f'BACKLIGHT:{lighting:.0f}')
                elif lighting > 18:
                    phone_indicators += 1
                    phone_reasons.append(f'backlight:{lighting:.0f}')
                
                if moire > 35:  # Strong screen pattern
                    phone_indicators += 1
                    strong_indicators += 1
                    phone_reasons.append(f'MOIRE:{moire:.0f}')
                elif moire > 22:
                    phone_indicators += 1
                    phone_reasons.append(f'moire:{moire:.0f}')
                
                # Supporting indicators (weaker signals)
                if reflection > 8:  # High reflection
                    phone_indicators += 1
                    phone_reasons.append(f'reflect:{reflection:.0f}')
                
                if saturation > 35:  # Very unusual color
                    phone_indicators += 1
                    phone_reasons.append(f'color:{saturation:.0f}')
                
                if texture > 250:  # Extremely high texture
                    phone_indicators += 1
                    phone_reasons.append(f'texture:{texture:.0f}')
                
                # Check size ratio
                face_area = w * h
                frame_area = frame.shape[0] * frame.shape[1]
                face_ratio = face_area / frame_area
                
                # Very small face = likely phone
                if face_ratio < 0.06:
                    phone_indicators += 1
                    phone_reasons.append(f'small:{face_ratio*100:.1f}%')
                
                # DECISION LOGIC: Need either strong evidence OR multiple weak indicators
                # Option 1: 2+ STRONG indicators = definitely phone
                # Option 2: 4+ total indicators = likely phone
                likely_phone = (strong_indicators >= 2) or (phone_indicators >= 4)
                
                face_result = {
                    'bbox': (x, y, w, h),
                    'is_real': is_real and not likely_phone,  # Override if phone detected
                    'confidence': confidence if not likely_phone else confidence * 0.3,  # Reduce if phone
                    'label': label if not likely_phone else 'Phone Screen',
                    'scores': scores,
                    'phone_indicators': phone_indicators,
                    'phone_reasons': phone_reasons,
                    'likely_phone': likely_phone
                }
                all_face_results.append(face_result)
            
            # Use the BEST (most real) face for main result
            real_faces = [f for f in all_face_results if f['is_real']]
            if real_faces:
                # Use highest confidence real face
                best_face = max(real_faces, key=lambda f: f['confidence'])
            else:
                # All faces are fake, use first one
                best_face = all_face_results[0]
            
            antispoof_result = {
                'face_detected': True,
                'is_real': best_face['is_real'],
                'confidence': best_face['confidence'],
                'label': best_face['label'],
                'scores': best_face['scores'],
                'phone_indicators': best_face['phone_indicators'],
                'likely_phone': best_face['likely_phone'],
                'all_faces': all_face_results  # Store all face results
            }
        else:
            antispoof_result = {
                'face_detected': False,
                'is_real': False,
                'confidence': 0.0,
                'label': 'No Face',
                'scores': {},
                'phone_indicators': 0,
                'likely_phone': False,
                'all_faces': []
            }
        
        result['mediapipe_result'] = mediapipe_result
        result['antispoof_result'] = antispoof_result
        
        # Step 3: Combined Decision Logic based on Security Level
        if self.security_level == 1:
            # Level 1: Anti-spoofing only
            result['verified'] = antispoof_result['is_real']
            result['combined_confidence'] = antispoof_result['confidence']
            result['verification_level'] = 'BASIC'
            result['message'] = 'Passive anti-spoofing check only'
            
        elif self.security_level == 2:
            # Level 2: MediaPipe OR Anti-spoofing (at least one must pass)
            mp_pass = mediapipe_result['is_live'] and mediapipe_result['has_face']
            as_pass = antispoof_result['is_real']
            
            result['verified'] = mp_pass or as_pass
            result['combined_confidence'] = max(
                mediapipe_result['liveness_score'],
                antispoof_result['confidence']
            )
            result['verification_level'] = 'STANDARD'
            
            if mp_pass and as_pass:
                result['message'] = '✅ Both checks passed'
            elif mp_pass:
                result['message'] = '✅ MediaPipe passed (Anti-spoofing uncertain)'
            elif as_pass:
                result['message'] = '✅ Anti-spoofing passed (No liveness detected yet)'
            else:
                result['message'] = '❌ Both checks failed'
                
        elif self.security_level == 3:
            # Level 3: MediaPipe AND Anti-spoofing (BOTH must pass)
            mp_pass = mediapipe_result['is_live'] and mediapipe_result['has_face']
            as_pass = antispoof_result['is_real']
            phone_detected = antispoof_result['likely_phone']
            
            result['verified'] = mp_pass and as_pass and not phone_detected
            result['combined_confidence'] = (
                mediapipe_result['liveness_score'] * 0.5 +
                antispoof_result['confidence'] * 0.5
            )
            result['verification_level'] = 'HIGH'
            
            # Detailed feedback
            if not mediapipe_result['has_face']:
                result['message'] = '❌ No face detected by MediaPipe'
            elif phone_detected:
                result['message'] = f'❌ PHONE SCREEN DETECTED ({antispoof_result["phone_indicators"]}/4 indicators)'
            elif not mp_pass and not as_pass:
                result['message'] = '❌ No liveness AND possible spoofing detected'
            elif not mp_pass:
                result['message'] = '⚠️ Waiting for liveness proof (blink or move head)'
            elif not as_pass:
                result['message'] = f'⚠️ Anti-spoofing failed (confidence: {antispoof_result["confidence"]:.1%})'
            else:
                result['message'] = '✅ VERIFIED: Live human face confirmed'
                
        elif self.security_level == 4:
            # Level 4: Maximum security with challenge requirements
            mp_pass = mediapipe_result['is_live'] and mediapipe_result['has_face']
            as_pass = antispoof_result['is_real']
            phone_detected = antispoof_result['likely_phone']
            
            # Require significant liveness proof
            has_blinked = mediapipe_result['blink_count'] >= 2
            has_moved = len(mediapipe_result['head_movements']) >= 2
            
            result['verified'] = (
                mp_pass and as_pass and not phone_detected and 
                has_blinked and has_moved
            )
            result['combined_confidence'] = (
                mediapipe_result['liveness_score'] * 0.5 +
                antispoof_result['confidence'] * 0.5
            )
            result['verification_level'] = 'MAXIMUM'
            
            # Challenge feedback
            challenges_met = []
            challenges_needed = []
            
            if has_blinked:
                challenges_met.append('✅ Blink')
            else:
                challenges_needed.append('👁️ Blink 2+ times')
                
            if has_moved:
                challenges_met.append('✅ Head movement')
            else:
                challenges_needed.append('🔄 Move head in 2+ directions')
                
            if as_pass and not phone_detected:
                challenges_met.append('✅ Real face')
            else:
                challenges_needed.append('🛡️ Not a screen/photo')
            
            if result['verified']:
                result['message'] = '✅ MAXIMUM SECURITY VERIFIED: ' + ' | '.join(challenges_met)
            else:
                result['message'] = '⚠️ Complete challenges: ' + ' | '.join(challenges_needed)
        
        # Add detailed breakdown
        result['details'] = [
            f"MediaPipe: {'✅ LIVE' if mediapipe_result['is_live'] else '❌ NOT LIVE'} ({mediapipe_result['liveness_score']:.1%})",
            f"Anti-spoofing: {'✅ REAL' if antispoof_result['is_real'] else '❌ FAKE'} ({antispoof_result['confidence']:.1%})",
            f"Phone indicators: {antispoof_result['phone_indicators']}/4",
            f"Blinks: {mediapipe_result['blink_count']}, Movements: {len(mediapipe_result['head_movements'])}"
        ]
        
        # Store in history
        self.verification_history.append(result)
        if len(self.verification_history) > 30:  # Keep last 30 results
            self.verification_history.pop(0)
        
        return result
    
    def draw_results(self, frame, result):
        """
        SIMPLIFIED: Draw only REAL or FAKE
        
        Args:
            frame: Input frame (BGR)
            result: Detection result dict
            
        Returns:
            Annotated frame with simple REAL/FAKE label
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]
        
        # Determine if REAL or FAKE
        antispoof_result = result.get('antispoof_result', {})
        mediapipe_result = result.get('mediapipe_result', {})
        
        # Simple logic: REAL = both pass, FAKE = either fails
        is_real = result.get('verified', False)
        
        # Check for phone screen specifically
        is_phone = antispoof_result.get('likely_phone', False)
        
        # DRAW BOUNDING BOXES FOR ALL FACES
        all_faces = antispoof_result.get('all_faces', [])
        
        if len(all_faces) > 0:
            # Draw box for EACH detected face
            for face_data in all_faces:
                x, y, w_box, h_box = face_data['bbox']
                face_is_real = face_data['is_real']
                face_is_phone = face_data['likely_phone']
                
                # Color coding for each face
                if face_is_real:
                    box_color = (0, 255, 0)  # GREEN = REAL
                    label_text = "REAL"
                else:
                    box_color = (0, 0, 255)  # RED = FAKE
                    if face_is_phone:
                        label_text = "FAKE (Phone)"
                    else:
                        label_text = "FAKE"
                
                # Draw thick bounding box
                cv2.rectangle(annotated, (x, y), (x+w_box, y+h_box), box_color, 5)
                
                # Draw label above face
                label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
                cv2.rectangle(annotated, (x, y-50), (x+label_size[0]+15, y), box_color, -1)
                cv2.putText(annotated, label_text, (x+8, y-18),
                           cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
                
                # Show phone indicators if detected
                if face_is_phone:
                    indicator_text = f"{face_data['phone_indicators']}/5"
                    cv2.putText(annotated, indicator_text, (x, y+h_box+25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
        
        # SIMPLE TOP STATUS
        if is_real:
            status_color = (0, 255, 0)  # Green
            status_bg = (0, 180, 0)
            status_text = "REAL PERSON"
        else:
            status_color = (0, 0, 255)  # Red
            status_bg = (0, 0, 180)
            status_text = "FAKE DETECTED"
        
        # Draw large status banner at top
        cv2.rectangle(annotated, (0, 0), (w, 80), status_bg, -1)
        
        # Center text
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_DUPLEX, 2.0, 4)[0]
        text_x = (w - text_size[0]) // 2
        
        cv2.putText(annotated, status_text, (text_x, 55),
                   cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 4)
        
        return annotated
    
    def get_statistics(self):
        """
        Get verification statistics from history
        
        Returns:
            Statistics dict
        """
        if not self.verification_history:
            return {
                'total_attempts': 0,
                'verified_count': 0,
                'success_rate': 0.0
            }
        
        total = len(self.verification_history)
        verified = sum(1 for r in self.verification_history if r['verified'])
        
        return {
            'total_attempts': total,
            'verified_count': verified,
            'rejected_count': total - verified,
            'success_rate': verified / total if total > 0 else 0.0,
            'avg_confidence': np.mean([r['combined_confidence'] for r in self.verification_history])
        }

