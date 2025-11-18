import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LiveAuthCamera from '../components/LiveAuthCamera';
import { authAPI } from '../api/config';
import './Login.css';

const Login = ({ setIsAuthenticated, setUser }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [userCount, setUserCount] = useState(0);
  const [recognitionThreshold, setRecognitionThreshold] = useState(0.6);
  const [securityLevel, setSecurityLevel] = useState(3);
  const [loginResult, setLoginResult] = useState(null);

  useEffect(() => {
    fetchUserCount();
  }, []);

  const fetchUserCount = async () => {
    try {
      const response = await authAPI.getUsersCount();
      setUserCount(response.data.count);
    } catch (err) {
      console.error('Error fetching user count:', err);
    }
  };

  const handleAuthStart = () => {
    setError('');
    setSuccess('');
    setLoginResult(null);
    setLoading(true);
  };

  const handleAuthComplete = (result) => {
    setLoading(false);
    setLoginResult(result);

    if (result.success) {
      setSuccess(result.message);
      setIsAuthenticated(true);
      setUser({
        id: result.user_id,
        name: result.user_name,
      });

      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } else {
      setError(result.message);
    }
  };

  const securityLevelMap = {
    1: 'Basic',
    2: 'Standard',
    3: 'High',
    4: 'Maximum',
  };

  if (userCount === 0) {
    return (
      <div className="login-container">
        <div className="login-card card fade-in">
          <div className="text-center">
            <h1>🔐 Face Authentication</h1>
            <div className="alert alert-warning mt-3">
              ⚠️ No registered users found. Please register first.
            </div>
            <button
              onClick={() => navigate('/register')}
              className="btn-primary w-100 mt-3"
            >
              Go to Registration →
            </button>
            <button
              onClick={() => navigate('/admin-login')}
              className="btn-secondary w-100 mt-3"
            >
              🔑 API Management
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className="login-card card fade-in">
        <h1 className="text-center">🔐 Secure Face Authentication</h1>
        <p className="text-center subtitle">Login with Face Recognition</p>

        <div className="info-badge">
          📊 {userCount} registered user(s) in database
        </div>

        <div className="login-grid">
          <div className="security-info">
            <h3>🛡️ Security Features</h3>
            <div className="feature-list">
              <div className="feature-item">
                <span className="feature-icon">✅</span>
                <div>
                  <strong>Face Recognition</strong>
                  <p>Identifies who you are</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">✅</span>
                <div>
                  <strong>Real-time Detection</strong>
                  <p>Continuous face monitoring</p>
                </div>
              </div>
            </div>

            <div className="settings-section">
              <h4>⚙️ Advanced Settings</h4>

              <label>
                Recognition Threshold: {(recognitionThreshold * 100).toFixed(0)}%
                <input
                  type="range"
                  min="40"
                  max="90"
                  value={recognitionThreshold * 100}
                  onChange={(e) => setRecognitionThreshold(e.target.value / 100)}
                  className="slider"
                />
                <small>Higher = More strict face matching</small>
              </label>

              <label className="mt-3">
                Security Level: {securityLevelMap[securityLevel]}
                <select
                  value={securityLevel}
                  onChange={(e) => setSecurityLevel(Number(e.target.value))}
                >
                  <option value={1}>Basic</option>
                  <option value={2}>Standard</option>
                  <option value={3}>High</option>
                  <option value={4}>Maximum</option>
                </select>
              </label>
            </div>

            <div className="instructions mt-3">
              <h4>📋 Instructions</h4>
              <ol>
                <li>Position your face clearly in the camera frame</li>
                <li>Click "Start Live Authentication (15s)"</li>
                <li>Stay in frame for authentication</li>
                <li>System continuously monitors and verifies your identity</li>
              </ol>
              <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: '#fff3cd', borderRadius: '6px', fontSize: '0.85rem' }}>
                ⚠️ <strong>Important:</strong> Camera monitors for 15 seconds continuously for face recognition.
              </div>
            </div>
          </div>

          <div className="camera-section">
            <h3>🔐 Live Authentication</h3>
            <LiveAuthCamera
              onAuthStart={handleAuthStart}
              onAuthComplete={handleAuthComplete}
              securityLevel={securityLevel}
              recognitionThreshold={recognitionThreshold}
            />

            {error && <div className="alert alert-danger mt-3">{error}</div>}
            {success && <div className="alert alert-success mt-3">{success}</div>}

            {loginResult && loginResult.annotated_image && (
              <div className="result-section mt-3">
                <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-navy)' }}>
                  {loginResult.success ? '✅ Authentication Result' : '❌ Detection Result'}
                </h4>
                <img
                  src={loginResult.annotated_image}
                  alt="Detection Result"
                  className="result-image"
                  style={{ border: `3px solid ${loginResult.success ? '#28a745' : '#dc3545'}` }}
                />
                <div className="detection-info">
                  {loginResult.face_count !== undefined && (
                    <div className="info-item">
                      <strong>Faces Detected:</strong> {loginResult.face_count}
                    </div>
                  )}
                  {loginResult.all_recognized_faces && loginResult.all_recognized_faces.length > 0 && (
                    <div className="info-item">
                      <strong>Recognized Users:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        {loginResult.all_recognized_faces.map((face, idx) => (
                          <li key={idx}>
                            {face.name} ({(face.confidence * 100).toFixed(1)}% match)
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="footer-actions">
          <button onClick={() => navigate('/register')} className="btn-secondary">
            New User? Register Here →
          </button>
          <button
            onClick={() => navigate('/admin-login')}
            className="btn-secondary"
            style={{ marginTop: '0.5rem' }}
          >
            🔑 API Management
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
