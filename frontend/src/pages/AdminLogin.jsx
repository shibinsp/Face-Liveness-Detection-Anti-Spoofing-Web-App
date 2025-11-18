import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const AdminLogin = () => {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Admin password check
    if (password === 'srini1205') {
      // Store admin session
      sessionStorage.setItem('adminAuth', 'true');
      setTimeout(() => {
        navigate('/api-management');
      }, 500);
    } else {
      setError('Invalid admin password');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card card fade-in" style={{ maxWidth: '500px', margin: '2rem auto' }}>
        <h1 className="text-center">🔑 Admin Login</h1>
        <p className="text-center subtitle">Enter admin password to access API Management</p>

        <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Admin Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                fontSize: '1rem',
                border: '2px solid var(--color-border)',
                borderRadius: '8px',
                outline: 'none',
              }}
            />
          </div>

          {error && (
            <div className="alert alert-danger" style={{ marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className="btn-primary w-100"
            style={{ padding: '0.75rem', fontSize: '1rem' }}
          >
            {loading ? 'Verifying...' : '🔓 Login as Admin'}
          </button>

          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary w-100 mt-3"
          >
            ← Back to Home
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
