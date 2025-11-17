import { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import './Camera.css';

const Camera = ({ onCapture, disabled = false }) => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user',
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImageSrc(imageSrc);
    if (onCapture) {
      onCapture(imageSrc);
    }
  }, [webcamRef, onCapture]);

  const retake = () => {
    setImageSrc(null);
    if (onCapture) {
      onCapture(null);
    }
  };

  return (
    <div className="camera-container">
      {!imageSrc ? (
        <>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="webcam"
          />
          <button
            onClick={capture}
            disabled={disabled}
            className="btn-primary w-100 mt-3"
          >
            📸 Capture Photo
          </button>
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

export default Camera;
