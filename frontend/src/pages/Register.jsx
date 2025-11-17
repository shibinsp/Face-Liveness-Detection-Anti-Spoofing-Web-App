import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Camera from '../components/Camera';
import { authAPI } from '../api/config';
import './Register.css';

const Register = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleCapture = (imageSrc) => {
    setImage(imageSrc);
    setError('');
    setSuccess('');
  };

  const handleRegister = async () => {
    if (!name.trim()) {
      setError('Please enter your name');
      return;
    }

    if (!image) {
      setError('Please capture your face');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await authAPI.register({
        name: name.trim(),
        email: email.trim() || null,
        image,
      });

      if (response.data.success) {
        setSuccess(response.data.message);

        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card card fade-in">
        <h1 className="text-center">🆕 User Registration</h1>
        <p className="text-center subtitle">Register with Face Recognition</p>

        <div className="register-grid">
          <div className="info-section">
            <h3>📝 Enter Your Information</h3>

            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email (Optional)</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                disabled={loading}
              />
            </div>

            <div className="instructions-box">
              <h4>📋 Instructions</h4>
              <ol>
                <li>Enter your name above</li>
                <li>Click "Capture Photo" to open your camera</li>
                <li>Look directly at the camera</li>
                <li>Make sure your face is well-lit and clearly visible</li>
                <li>Click "Register" to complete registration</li>
              </ol>
            </div>

            <div className="info-box mt-3">
              <h4>🔒 Privacy & Security</h4>
              <ul>
                <li>✅ Face embeddings stored securely</li>
                <li>✅ Original images encrypted</li>
                <li>✅ No data shared with third parties</li>
                <li>✅ GDPR compliant storage</li>
              </ul>
            </div>
          </div>

          <div className="camera-section">
            <h3>📸 Face Capture</h3>
            <Camera onCapture={handleCapture} disabled={loading} />

            {error && <div className="alert alert-danger mt-3">{error}</div>}
            {success && <div className="alert alert-success mt-3">{success}</div>}

            {image && (
              <button
                onClick={handleRegister}
                disabled={loading}
                className="btn-success w-100 mt-3"
              >
                {loading ? '🔄 Registering...' : '✅ Register with this photo'}
              </button>
            )}
          </div>
        </div>

        <div className="footer-actions">
          <button
            onClick={() => navigate('/')}
            disabled={loading}
            className="btn-secondary"
          >
            ← Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default Register;
