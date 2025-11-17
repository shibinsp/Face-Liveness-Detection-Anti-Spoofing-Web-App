import { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './Camera.css';

const CameraWithLiveDetection = ({ onCapture, disabled = false, securityLevel = 3 }) => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [liveStatus, setLiveStatus] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const intervalRef = useRef(null);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user',
  };

  // Real-time detection while camera is active
  useEffect(() => {
    if (!imageSrc) {
      // Start live detection every 1.5 seconds
      const timer = setInterval(() => {
        if (webcamRef.current && !isDetecting) {
          detectLiveFace();
        }
      }, 1500); // Check every 1.5 seconds

      intervalRef.current = timer;

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    } else {
      // Stop live detection when image is captured
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageSrc, isDetecting]);

  const detectLiveFace = async () => {
    if (isDetecting || !webcamRef.current) return;

    try {
      setIsDetecting(true);
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return;

      const formData = new FormData();
      formData.append('image', screenshot);
      formData.append('security_level', securityLevel);

      const response = await axios.post('http://localhost:8021/api/detect-live', formData);
      const result = response.data;

      setLiveStatus(result);
    } catch (error) {
      console.error('Live detection error:', error);
    } finally {
      setIsDetecting(false);
    }
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImageSrc(imageSrc);
    setLiveStatus(null);
    if (onCapture) {
      onCapture(imageSrc);
    }
  }, [webcamRef, onCapture]);

  const retake = () => {
    setImageSrc(null);
    setLiveStatus(null);
    if (onCapture) {
      onCapture(null);
    }
  };

  // Get status color based on detection result
  const getStatusColor = () => {
    if (!liveStatus) return '#666';
    switch (liveStatus.status) {
      case 'REAL':
        return '#28a745'; // Green
      case 'PHONE_SCREEN':
      case 'FAKE':
        return '#dc3545'; // Red
      case 'WAITING_LIVENESS':
        return '#ffc107'; // Yellow
      default:
        return '#666'; // Gray
    }
  };

  return (
    <div className="camera-container">
      {!imageSrc ? (
        <>
          <div className="live-camera-wrapper" style={{ position: 'relative' }}>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="webcam"
            />

          </div>

          <button
            onClick={capture}
            disabled={disabled}
            className="btn-primary w-100 mt-3"
          >
            📸 Capture Photo
          </button>

          {/* Instructions based on live status */}
          {liveStatus && liveStatus.status === 'REAL' && (
            <div className="alert alert-success mt-3" style={{ fontSize: '0.85rem' }}>
              ✅ Ready to capture! Click "Capture Photo" when ready.
            </div>
          )}
        </>
      ) : (
        <>
          <img src={imageSrc} alt="Captured" className="captured-image" />
          <button onClick={retake} className="btn-secondary w-100 mt-3">
            🔄 Retake Photo
          </button>
        </>
      )}
    </div>
  );
};

export default CameraWithLiveDetection;
