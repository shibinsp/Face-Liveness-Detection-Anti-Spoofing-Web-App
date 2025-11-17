import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/config';
import './Dashboard.css';

const Dashboard = ({ user, setIsAuthenticated }) => {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);
  const [loginHistory, setLoginHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !user.id) {
      navigate('/');
      return;
    }

    fetchUserData();
  }, [user, navigate]);

  const fetchUserData = async () => {
    try {
      const [userResponse, historyResponse] = await Promise.all([
        authAPI.getUser(user.id),
        authAPI.getLoginHistory(user.id, 20),
      ]);

      setUserInfo(userResponse.data);
      setLoginHistory(historyResponse.data.history);
    } catch (err) {
      console.error('Error fetching user data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate('/');
  };

  // Prevent showing logout button in sidebar since it's in header
  const showSidebarLogout = false;

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!userInfo) {
    return (
      <div className="dashboard-container">
        <div className="alert alert-danger">Error loading user data</div>
      </div>
    );
  }

  const successfulLogins = loginHistory.filter((h) => h.status === 'success').length;

  return (
    <div className="dashboard-container fade-in">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>👋 Welcome, {userInfo.name}!</h1>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="sidebar">
          <div className="user-profile">
            {userInfo.profile_image && (
              <img
                src={userInfo.profile_image}
                alt={userInfo.name}
                className="profile-image"
              />
            )}
            <h3>{userInfo.name}</h3>
            {userInfo.email && <p className="user-email">{userInfo.email}</p>}
            <p className="user-meta">Member Since: {userInfo.created_at?.slice(0, 10)}</p>

            {showSidebarLogout && (
              <button onClick={handleLogout} className="btn-danger w-100 mt-3">
                🚪 Logout
              </button>
            )}
          </div>

          <div className="quick-stats">
            <div className="stat-item">
              <div className="stat-label">User ID</div>
              <div className="stat-value">#{String(userInfo.id).padStart(4, '0')}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Total Logins</div>
              <div className="stat-value">{loginHistory.length}</div>
            </div>
            {userInfo.last_login && (
              <div className="stat-item">
                <div className="stat-label">Last Login</div>
                <div className="stat-value-small">
                  {userInfo.last_login?.slice(0, 19).replace('T', ' ')}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="main-content">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              📜 Login History
            </button>
            <button
              className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              ⚙️ Settings
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'dashboard' && (
              <div className="dashboard-tab">
                <h2>Dashboard</h2>

                <div className="status-card">
                  <div className="status-header">
                    <span className="status-icon">✅</span>
                    <h3>Authentication Status</h3>
                  </div>
                  <div className="status-value">VERIFIED</div>
                </div>

                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon">🔐</div>
                    <h4>Face Recognition</h4>
                    <p>Advanced face detection and recognition using YOLO v11 and DeepFace</p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">👁️</div>
                    <h4>Liveness Detection</h4>
                    <p>Real-time verification using MediaPipe to ensure you're a live person</p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">🛡️</div>
                    <h4>Anti-Spoofing</h4>
                    <p>10+ metrics to detect photos, videos, and phone screen attacks</p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">🔒</div>
                    <h4>Multi-Factor Auth</h4>
                    <p>Combines face recognition, liveness, and anti-spoofing protection</p>
                  </div>
                </div>

                <div className="info-section">
                  <h3>System Information</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <strong>User ID:</strong> #{String(userInfo.id).padStart(4, '0')}
                    </div>
                    <div className="info-item">
                      <strong>Account Created:</strong> {userInfo.created_at?.slice(0, 10)}
                    </div>
                    <div className="info-item">
                      <strong>Successful Logins:</strong> {successfulLogins}
                    </div>
                    <div className="info-item">
                      <strong>Security Level:</strong> High
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="history-tab">
                <h2>Login History</h2>

                {loginHistory.length > 0 ? (
                  <>
                    <div className="history-stats">
                      <div className="stat-card">
                        <div className="stat-number">{loginHistory.length}</div>
                        <div className="stat-label">Total Attempts</div>
                      </div>
                      <div className="stat-card success">
                        <div className="stat-number">{successfulLogins}</div>
                        <div className="stat-label">Successful</div>
                      </div>
                      <div className="stat-card danger">
                        <div className="stat-number">
                          {loginHistory.length - successfulLogins}
                        </div>
                        <div className="stat-label">Failed</div>
                      </div>
                    </div>

                    <div className="history-table">
                      <table>
                        <thead>
                          <tr>
                            <th>Login Time</th>
                            <th>Liveness Score</th>
                            <th>Confidence Score</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {loginHistory.map((record) => (
                            <tr key={record.id}>
                              <td>
                                {record.login_time?.slice(0, 19).replace('T', ' ')}
                              </td>
                              <td>
                                {record.liveness_score > 0
                                  ? `${(record.liveness_score * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </td>
                              <td>
                                {record.confidence_score > 0
                                  ? `${(record.confidence_score * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </td>
                              <td>
                                <span
                                  className={`status-badge ${record.status}`}
                                >
                                  {record.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                ) : (
                  <div className="alert alert-info">No login history yet.</div>
                )}
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="settings-tab">
                <h2>Account Settings</h2>

                <div className="settings-section">
                  <h3>Profile Information</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <strong>Name:</strong> {userInfo.name}
                    </div>
                    <div className="info-item">
                      <strong>Email:</strong> {userInfo.email || 'Not provided'}
                    </div>
                  </div>
                </div>

                <div className="settings-section">
                  <h3>Security Settings</h3>
                  <div className="alert alert-info">
                    🚧 Advanced security settings coming soon!
                  </div>
                </div>

                <div className="settings-section danger-zone">
                  <h3>Danger Zone</h3>
                  <p>
                    Deleting your account will permanently remove all your data, including
                    face embeddings and login history. This action cannot be undone.
                  </p>
                  <button className="btn-danger">🗑️ Delete Account</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
