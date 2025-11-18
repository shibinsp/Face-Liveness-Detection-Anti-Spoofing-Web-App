import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-section footer-about">
          <div className="footer-logo">
            <span className="footer-logo-icon">🔐</span>
            <h3>Face Auth System</h3>
          </div>
          <p className="footer-description">
            Advanced face authentication with liveness detection and anti-spoofing protection.
            Secure, fast, and reliable biometric authentication.
          </p>
        </div>

        <div className="footer-section footer-features">
          <h4>Features</h4>
          <ul>
            <li>
              <span className="feature-icon">🔐</span>
              Face Recognition
            </li>
            <li>
              <span className="feature-icon">👁️</span>
              Liveness Detection
            </li>
            <li>
              <span className="feature-icon">🛡️</span>
              Anti-Spoofing
            </li>
            <li>
              <span className="feature-icon">🔒</span>
              Multi-Factor Auth
            </li>
            <li>
              <span className="feature-icon">📊</span>
              Real-time Analytics
            </li>
          </ul>
        </div>

        <div className="footer-section footer-security">
          <h4>Security</h4>
          <ul>
            <li>
              <span className="feature-icon">🔑</span>
              256-bit Encryption
            </li>
            <li>
              <span className="feature-icon">🗄️</span>
              Secure Database
            </li>
            <li>
              <span className="feature-icon">📸</span>
              Phone Screen Detection
            </li>
            <li>
              <span className="feature-icon">🎯</span>
              95%+ Accuracy
            </li>
            <li>
              <span className="feature-icon">⚡</span>
              Real-time Processing
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <div className="footer-copyright">
            <p>
              &copy; {currentYear} Face Authentication System. All rights reserved.
            </p>
            <p className="footer-subtitle">
              Built with React, FastAPI, and Machine Learning
            </p>
          </div>

          <div className="footer-links">
            <a href="#privacy" className="footer-link">Privacy Policy</a>
            <span className="footer-separator">•</span>
            <a href="#terms" className="footer-link">Terms of Service</a>
            <span className="footer-separator">•</span>
            <a href="#security" className="footer-link">Security</a>
            <span className="footer-separator">•</span>
            <a href="#contact" className="footer-link">Contact</a>
          </div>

          <div className="footer-social">
            <div className="footer-version">
              <span className="version-label">Version</span>
              <span className="version-number">2.0.0</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
