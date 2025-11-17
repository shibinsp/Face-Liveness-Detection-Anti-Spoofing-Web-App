import { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './Camera.css';

const LiveAuthCamera = ({ onAuthStart, onAuthComplete, securityLevel = 3, recognitionThreshold = 0.6 }) => {
  const webcamRef = useRef(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authProgress, setAuthProgress] = useState(0);
  const [currentStatus, setCurrentStatus] = useState('');
  const [detectionResults, setDetectionResults] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(30);
  const intervalRef = useRef(null);
  const authStartTimeRef = useRef(null);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user',
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const checkFrame = async () => {
    if (!webcamRef.current) return null;

    try {
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return null;

      const formData = new FormData();
      formData.append('image', screenshot);
      formData.append('security_level', securityLevel);

      const response = await axios.post('http://localhost:8000/api/detect-live', formData);
      return response.data;
    } catch (error) {
      console.error('Frame check error:', error);
      return null;
    }
  };

  const attemptLogin = async () => {
    if (!webcamRef.current) return null;

    try {
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return null;

      const formData = new FormData();
      formData.append('image', screenshot);
      formData.append('recognition_threshold', recognitionThreshold);
      formData.append('security_level', securityLevel);

      const response = await axios.post('http://localhost:8000/api/login', formData);
      return response.data;
    } catch (error) {
      console.error('Login attempt error:', error);
      return null;
    }
  };

  const startAuthentication = useCallback(() => {
    if (isAuthenticating) return;

    console.log('Starting live authentication...');

    setIsAuthenticating(true);
    setAuthProgress(0);
    setDetectionResults([]);
    setTimeRemaining(15);
    setCurrentStatus('🔍 Initializing detection...');
    authStartTimeRef.current = Date.now();

    if (onAuthStart) {
      onAuthStart();
    }

    let passedFrames = 0;
    let totalFrames = 0;
    let hasRealFace = false;
    let consecutivePasses = 0;
    let loginAttempted = false;

    // Async monitoring function
    const performCheck = async () => {
      try {
        const elapsed = (Date.now() - authStartTimeRef.current) / 1000;
        const remaining = Math.max(0, 15 - elapsed);
        setTimeRemaining(Math.ceil(remaining));
        setAuthProgress((elapsed / 15) * 100);

        console.log(`Frame check at ${elapsed.toFixed(1)}s, remaining: ${remaining.toFixed(1)}s`);

        if (elapsed >= 15) {
          // Time's up
          console.log('Time limit reached');
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          setIsAuthenticating(false);

          const successRate = totalFrames > 0 ? (passedFrames / totalFrames) * 100 : 0;

          console.log(`Final results: hasRealFace=${hasRealFace}, successRate=${successRate.toFixed(0)}%`);

          if (hasRealFace && successRate >= 60) {
            setCurrentStatus('✅ Verification complete! Attempting login...');

            // Try to login
            const loginResult = await attemptLogin();

            if (loginResult && onAuthComplete) {
              onAuthComplete(loginResult);
            }
          } else {
            // Determine what's missing
            let failureReason = '';
            if (!hasRealFace) {
              failureReason = 'No face detected';
            } else if (successRate < 60) {
              failureReason = `Success rate too low: ${successRate.toFixed(0)}% (need 60%+)`;
            }

            setCurrentStatus(`❌ Verification failed: ${failureReason}`);

            if (onAuthComplete) {
              onAuthComplete({
                success: false,
                message: `❌ Authentication failed: ${failureReason}\n\nResults:\n• Face detected: ${hasRealFace ? '✅ YES' : '❌ NO'}\n• Success rate: ${successRate.toFixed(0)}% (need 60%+)\n• Frames analyzed: ${passedFrames}/${totalFrames}`,
              });
            }
          }

          return;
        }

        // Check current frame
        const result = await checkFrame();

        if (result) {
          totalFrames++;
          console.log(`Frame ${totalFrames}: is_real=${result.is_real}, is_live=${result.is_live}, phone=${result.phone_detected}`);

          setDetectionResults(prev => [...prev.slice(-9), result]); // Keep last 10 results

          // Check if this frame passed
          const framePassed = result.is_real;

          if (framePassed) {
            passedFrames++;
            consecutivePasses++;
            hasRealFace = true;

            // If we have 5 consecutive passes, try to login early
            if (consecutivePasses >= 5 && !loginAttempted && elapsed >= 5) {
              loginAttempted = true;
              setCurrentStatus('✅ Strong verification! Attempting login...');

              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }
              setIsAuthenticating(false);

              const loginResult = await attemptLogin();

              if (loginResult && onAuthComplete) {
                onAuthComplete(loginResult);
              }
              return;
            }
          } else {
            consecutivePasses = 0;
            setCurrentStatus('🔍 Detecting... Please stay in frame');
          }

          // Update status message
          const successRate = totalFrames > 0 ? (passedFrames / totalFrames) * 100 : 0;

          if (framePassed) {
            setCurrentStatus(`✅ Verification in progress... ${successRate.toFixed(0)}% success (${passedFrames}/${totalFrames})`);
          }
        }
      } catch (error) {
        console.error('Error in performCheck:', error);
      }
    };

    // Start monitoring interval
    const monitoringInterval = setInterval(() => {
      performCheck();
    }, 1000); // Check every 1 second

    intervalRef.current = monitoringInterval;

    // Perform first check immediately
    performCheck();
  }, [isAuthenticating, onAuthStart, onAuthComplete, recognitionThreshold, securityLevel]);

  const cancelAuthentication = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsAuthenticating(false);
    setAuthProgress(0);
    setCurrentStatus('');
    setDetectionResults([]);
  };

  // Get the most recent detection status
  const latestResult = detectionResults[detectionResults.length - 1];

  return (
    <div className="camera-container">
      <div style={{ position: 'relative' }}>
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          className="webcam"
        />

        {isAuthenticating && (
          <>
            {/* Progress bar */}
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '8px',
              background: 'rgba(0,0,0,0.5)',
              borderRadius: '0 0 8px 8px',
            }}>
              <div style={{
                height: '100%',
                width: `${authProgress}%`,
                background: 'linear-gradient(90deg, #28a745, #20c997)',
                transition: 'width 0.3s ease',
              }} />
            </div>

            {/* Timer overlay */}
            <div style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              background: 'rgba(0,0,0,0.8)',
              color: 'white',
              padding: '8px 12px',
              borderRadius: '20px',
              fontWeight: 'bold',
              fontSize: '1rem',
            }}>
              ⏱️ {timeRemaining}s
            </div>

            {/* Status overlay */}
            {currentStatus && (
              <div style={{
                position: 'absolute',
                top: '10px',
                left: '10px',
                right: '60px',
                background: 'rgba(0,0,0,0.8)',
                color: 'white',
                padding: '10px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: 'bold',
              }}>
                {currentStatus}
              </div>
            )}

          </>
        )}
      </div>

      {/* Live stats */}
      {isAuthenticating && latestResult && (
        <div style={{
          marginTop: '10px',
          padding: '10px',
          background: 'var(--color-light-blue)',
          borderRadius: '8px',
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          fontSize: '0.8rem',
        }}>
          <div>
            <strong>Faces Detected:</strong> {latestResult.face_count || (latestResult.is_real ? 1 : 0)}
          </div>
          <div>
            <strong>Frames:</strong> {detectionResults.length}
          </div>
        </div>
      )}

      {!isAuthenticating ? (
        <button
          onClick={startAuthentication}
          className="btn-success w-100 mt-3"
          style={{ fontSize: '1rem', padding: '12px' }}
        >
          🔐 Start Live Authentication (15s)
        </button>
      ) : (
        <button
          onClick={cancelAuthentication}
          className="btn-secondary w-100 mt-3"
        >
          ⏹️ Cancel
        </button>
      )}

      <div style={{
        marginTop: '10px',
        padding: '10px',
        background: 'var(--color-light-blue)',
        borderRadius: '8px',
        fontSize: '0.8rem',
        textAlign: 'center',
      }}>
        💡 <strong>How it works:</strong> Camera monitors continuously for 15 seconds to detect and authenticate your face.
      </div>
    </div>
  );
};

export default LiveAuthCamera;
