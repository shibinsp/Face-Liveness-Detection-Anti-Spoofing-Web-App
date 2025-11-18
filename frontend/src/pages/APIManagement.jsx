import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

const APIManagement = () => {
  const navigate = useNavigate();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyDescription, setNewKeyDescription] = useState('');
  const [createdKey, setCreatedKey] = useState(null);
  const [usageStats, setUsageStats] = useState({});

  useEffect(() => {
    // Check admin authentication
    const adminAuth = sessionStorage.getItem('adminAuth');
    if (!adminAuth) {
      navigate('/admin-login');
      return;
    }

    fetchAPIKeys();
    fetchUsageStats();
  }, [navigate]);

  const fetchAPIKeys = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8021/api/admin/api-keys');
      setApiKeys(response.data.api_keys || []);
      setError('');
    } catch (err) {
      setError('Failed to load API keys');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageStats = async () => {
    try {
      const response = await axios.get('http://localhost:8021/api/admin/api-usage');
      setUsageStats(response.data.usage || {});
    } catch (err) {
      console.error('Failed to load usage stats:', err);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await axios.post('http://localhost:8021/api/admin/api-keys', {
        name: newKeyName,
        description: newKeyDescription,
      });

      setCreatedKey(response.data.key);
      setSuccess('API Key created successfully!');
      setNewKeyName('');
      setNewKeyDescription('');
      fetchAPIKeys();
    } catch (err) {
      setError('Failed to create API key');
      console.error(err);
    }
  };

  const handleDeleteKey = async (keyPrefix) => {
    if (!window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:8021/api/admin/api-keys/${keyPrefix}`);
      setSuccess('API Key deleted successfully');
      fetchAPIKeys();
      fetchUsageStats();
    } catch (err) {
      setError('Failed to delete API key');
      console.error(err);
    }
  };

  const handleToggleKeyStatus = async (keyPrefix, currentStatus) => {
    try {
      await axios.patch(`http://localhost:8021/api/admin/api-keys/${keyPrefix}`, {
        active: !currentStatus,
      });
      setSuccess(`API Key ${currentStatus ? 'deactivated' : 'activated'} successfully`);
      fetchAPIKeys();
    } catch (err) {
      setError('Failed to update API key status');
      console.error(err);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('adminAuth');
    navigate('/');
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('API Key copied to clipboard!');
    setTimeout(() => setSuccess(''), 3000);
  };

  const maskKey = (key) => {
    if (!key) return '';
    if (key.length <= 12) return '****';
    return `${key.substring(0, 8)}${'*'.repeat(key.length - 12)}${key.substring(key.length - 4)}`;
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-card card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1>🔑 API Management Dashboard</h1>
            <p className="subtitle">Manage API keys and monitor usage</p>
          </div>
          <button onClick={handleLogout} className="btn-secondary">
            🚪 Logout
          </button>
        </div>

        {error && (
          <div className="alert alert-danger" style={{ marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success" style={{ marginBottom: '1rem' }}>
            {success}
          </div>
        )}

        {createdKey && (
          <div className="alert" style={{
            marginBottom: '1rem',
            background: '#d4edda',
            border: '2px solid #28a745',
            padding: '1.5rem'
          }}>
            <h4 style={{ marginBottom: '1rem', color: '#155724' }}>✅ New API Key Created</h4>
            <p style={{ marginBottom: '0.5rem', fontWeight: 'bold' }}>⚠️ Save this key now - you won't be able to see it again!</p>
            <div style={{
              background: '#fff',
              padding: '1rem',
              borderRadius: '6px',
              fontFamily: 'monospace',
              wordBreak: 'break-all',
              marginBottom: '0.5rem'
            }}>
              {createdKey}
            </div>
            <button
              onClick={() => copyToClipboard(createdKey)}
              className="btn-primary"
              style={{ marginTop: '0.5rem' }}
            >
              📋 Copy to Clipboard
            </button>
          </div>
        )}

        <div style={{ marginBottom: '2rem' }}>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-success"
          >
            {showCreateForm ? '❌ Cancel' : '➕ Create New API Key'}
          </button>
        </div>

        {showCreateForm && (
          <form onSubmit={handleCreateKey} className="card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Create New API Key</h3>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                Name *
              </label>
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Production Key, Development Key"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  border: '2px solid var(--color-border)',
                  borderRadius: '8px',
                }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                Description
              </label>
              <textarea
                value={newKeyDescription}
                onChange={(e) => setNewKeyDescription(e.target.value)}
                placeholder="Optional description for this API key"
                rows="3"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  border: '2px solid var(--color-border)',
                  borderRadius: '8px',
                }}
              />
            </div>

            <button type="submit" className="btn-success">
              🔐 Generate API Key
            </button>
          </form>
        )}

        <h2 style={{ marginBottom: '1rem' }}>📊 API Keys ({apiKeys.length})</h2>

        {loading ? (
          <div className="text-center" style={{ padding: '2rem' }}>
            <p>Loading API keys...</p>
          </div>
        ) : apiKeys.length === 0 ? (
          <div className="alert" style={{ background: '#f8f9fa' }}>
            No API keys found. Create your first API key to get started.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              background: 'white',
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <thead>
                <tr style={{ background: 'var(--color-navy)', color: 'white' }}>
                  <th style={{ padding: '1rem', textAlign: 'left' }}>Name</th>
                  <th style={{ padding: '1rem', textAlign: 'left' }}>API Key</th>
                  <th style={{ padding: '1rem', textAlign: 'left' }}>Created</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Usage</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((keyData, index) => {
                  const keyPrefix = keyData.key ? keyData.key.substring(0, 8) : '';
                  const usage = usageStats[keyPrefix] || 0;

                  return (
                    <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '1rem' }}>
                        <strong>{keyData.name || 'Unnamed'}</strong>
                        {keyData.description && (
                          <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
                            {keyData.description}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '1rem', fontFamily: 'monospace', fontSize: '0.9rem' }}>
                        {maskKey(keyData.key)}
                      </td>
                      <td style={{ padding: '1rem', fontSize: '0.9rem' }}>
                        {keyData.created_at ? new Date(keyData.created_at).toLocaleDateString() : 'N/A'}
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center' }}>
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.85rem',
                          fontWeight: 'bold',
                          background: keyData.active ? '#d4edda' : '#f8d7da',
                          color: keyData.active ? '#155724' : '#721c24',
                        }}>
                          {keyData.active ? '✅ Active' : '❌ Inactive'}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center', fontSize: '1.1rem', fontWeight: 'bold' }}>
                        {usage.toLocaleString()} requests
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                          <button
                            onClick={() => handleToggleKeyStatus(keyPrefix, keyData.active)}
                            className={keyData.active ? 'btn-secondary' : 'btn-success'}
                            style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                          >
                            {keyData.active ? '⏸️ Deactivate' : '▶️ Activate'}
                          </button>
                          <button
                            onClick={() => handleDeleteKey(keyPrefix)}
                            className="btn-danger"
                            style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                          >
                            🗑️ Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>📝 Usage Instructions</h3>
          <p style={{ marginBottom: '0.5rem' }}>To use an API key, include it in the request header:</p>
          <code style={{
            display: 'block',
            padding: '1rem',
            background: '#fff',
            borderRadius: '6px',
            fontFamily: 'monospace'
          }}>
            X-API-Key: your_api_key_here
          </code>
        </div>
      </div>
    </div>
  );
};

export default APIManagement;
