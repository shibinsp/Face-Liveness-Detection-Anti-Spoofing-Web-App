import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = ({ isAuthenticated, userName, onLogout }) => {
  const navigate = useNavigate();

  const handleLogoClick = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/');
    }
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo" onClick={handleLogoClick}>
            <div className="logo-icon">🔐</div>
            <div className="logo-text">
              <h1>Face Auth</h1>
              <span className="logo-tagline">Secure Authentication System</span>
            </div>
          </div>
        </div>

        <nav className="header-nav">
          <div className="nav-links">
            {!isAuthenticated ? (
              <>
                <button onClick={() => navigate('/')} className="nav-link">
                  <span className="nav-icon">🏠</span>
                  Login
                </button>
                <button onClick={() => navigate('/register')} className="nav-link">
                  <span className="nav-icon">📝</span>
                  Register
                </button>
              </>
            ) : (
              <>
                <button onClick={() => navigate('/dashboard')} className="nav-link">
                  <span className="nav-icon">📊</span>
                  Dashboard
                </button>
                <div className="user-info">
                  <span className="user-icon">👤</span>
                  <span className="user-name">{userName}</span>
                </div>
                <button onClick={onLogout} className="nav-link logout-btn">
                  <span className="nav-icon">🚪</span>
                  Logout
                </button>
              </>
            )}
          </div>
        </nav>

        <div className="header-right">
          <div className="security-badge">
            <span className="badge-icon">🛡️</span>
            <span className="badge-text">Secured</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
