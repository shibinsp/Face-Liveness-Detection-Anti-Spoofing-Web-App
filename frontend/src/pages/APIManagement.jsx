import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

const APIManagement = () => {
  const navigate = useNavigate();
  const [apiKeys, setApiKeys] = useState([]);
  const [filteredKeys, setFilteredKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Form states
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyDescription, setNewKeyDescription] = useState('');
  const [newKeyExpiryDays, setNewKeyExpiryDays] = useState('');
  const [newKeyRateLimit, setNewKeyRateLimit] = useState('');
  const [createdKey, setCreatedKey] = useState(null);

  // Usage states
  const [usageStats, setUsageStats] = useState({});
  const [timeline, setTimeline] = useState({});

  // UI states
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showKey, setShowKey] = useState({});
  const [selectedKeyLogs, setSelectedKeyLogs] = useState(null);
  const [viewingLogs, setViewingLogs] = useState(false);

  useEffect(() => {
    // Check admin authentication
    const adminAuth = sessionStorage.getItem('adminAuth');
    if (!adminAuth) {
      navigate('/admin-login');
      return;
    }

    fetchAPIKeys();
    fetchUsageStats();
    fetchTimeline();
  }, [navigate]);

  useEffect(() => {
    // Apply search and filter
    let filtered = [...apiKeys];

    // Search
    if (searchTerm) {
      filtered = filtered.filter(key =>
        key.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        key.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (filterStatus === 'active') {
      filtered = filtered.filter(key => key.active);
    } else if (filterStatus === 'inactive') {
      filtered = filtered.filter(key => !key.active);
    } else if (filterStatus === 'expired') {
      filtered = filtered.filter(key => {
        if (!key.expiry_date) return false;
        return new Date(key.expiry_date) < new Date();
      });
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'created_at') {
        return new Date(b.created_at) - new Date(a.created_at);
      } else if (sortBy === 'name') {
        return (a.name || '').localeCompare(b.name || '');
      } else if (sortBy === 'usage') {
        const usageA = usageStats[a.key?.substring(0, 8)] || 0;
        const usageB = usageStats[b.key?.substring(0, 8)] || 0;
        return usageB - usageA;
      }
      return 0;
    });

    setFilteredKeys(filtered);
  }, [apiKeys, searchTerm, sortBy, filterStatus, usageStats]);

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

  const fetchTimeline = async () => {
    try {
      const response = await axios.get('http://localhost:8021/api/admin/api-timeline?days=7');
      setTimeline(response.data.timeline || {});
    } catch (err) {
      console.error('Failed to load timeline:', err);
    }
  };

  const fetchKeyLogs = async (keyPrefix) => {
    try {
      const response = await axios.get(`http://localhost:8021/api/admin/api-logs/${keyPrefix}?limit=50`);
      setSelectedKeyLogs({
        keyPrefix,
        logs: response.data.logs || [],
        count: response.data.count || 0
      });
      setViewingLogs(true);
    } catch (err) {
      setError('Failed to load logs');
      console.error(err);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const payload = {
        name: newKeyName,
        description: newKeyDescription
      };

      if (newKeyExpiryDays) {
        payload.expiry_days = parseInt(newKeyExpiryDays);
      }

      if (newKeyRateLimit) {
        payload.rate_limit = parseInt(newKeyRateLimit);
      }

      const response = await axios.post('http://localhost:8021/api/admin/api-keys', payload);

      setCreatedKey(response.data.key);
      setSuccess('API Key created successfully!');
      setNewKeyName('');
      setNewKeyDescription('');
      setNewKeyExpiryDays('');
      setNewKeyRateLimit('');
      fetchAPIKeys();
      fetchUsageStats();
    } catch (err) {
      setError('Failed to create API key');
      console.error(err);
    }
  };

  const handleDeleteKey = async (keyPrefix, keyName) => {
    if (!window.confirm(`Are you sure you want to delete the API key "${keyName}"?\n\nThis action cannot be undone and will immediately revoke access for all applications using this key.`)) {
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

  const toggleKeyVisibility = (keyPrefix) => {
    setShowKey(prev => ({ ...prev, [keyPrefix]: !prev[keyPrefix] }));
  };

  const getKeyStatus = (keyData) => {
    if (!keyData.active) return { label: 'Inactive', color: '#dc3545' };
    if (keyData.expiry_date && new Date(keyData.expiry_date) < new Date()) {
      return { label: 'Expired', color: '#fd7e14' };
    }
    return { label: 'Active', color: '#28a745' };
  };

  const calculateDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return null;
    const days = Math.ceil((new Date(expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  };

  // Simple chart component
  const UsageChart = ({ data }) => {
    const maxValue = Math.max(...Object.values(data).map(d => Object.values(d).reduce((a, b) => a + b, 0)), 1);
    const dates = Object.keys(data).sort().slice(-7);

    return (
      <div style={{ padding: '1rem', background: 'white', borderRadius: '8px', marginTop: '1rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>📊 Usage Timeline (Last 7 Days)</h3>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end', height: '200px' }}>
          {dates.map(date => {
            const total = Object.values(data[date] || {}).reduce((a, b) => a + b, 0);
            const height = (total / maxValue) * 100;

            return (
              <div key={date} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'flex-end',
                  width: '100%'
                }}>
                  <div style={{
                    height: `${height}%`,
                    background: 'linear-gradient(180deg, #4CAF50, #45a049)',
                    borderRadius: '4px 4px 0 0',
                    minHeight: total > 0 ? '2px' : '0',
                    position: 'relative',
                    cursor: 'pointer'
                  }} title={`${total} requests`}>
                    {total > 0 && (
                      <div style={{
                        position: 'absolute',
                        top: '-20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontSize: '0.7rem',
                        fontWeight: 'bold',
                        color: '#4CAF50'
                      }}>
                        {total}
                      </div>
                    )}
                  </div>
                </div>
                <div style={{ fontSize: '0.65rem', marginTop: '0.5rem', transform: 'rotate(-45deg)', whiteSpace: 'nowrap' }}>
                  {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-card card">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1>🔑 API Management Dashboard</h1>
            <p className="subtitle">Manage API keys and monitor usage</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <a
              href="http://localhost:8021/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
              style={{ textDecoration: 'none', padding: '0.5rem 1rem' }}
            >
              📚 API Docs
            </a>
            <button onClick={handleLogout} className="btn-secondary">
              🚪 Logout
            </button>
          </div>
        </div>

        {/* Alerts */}
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

        {/* Created Key Alert */}
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
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => copyToClipboard(createdKey)}
                className="btn-primary"
              >
                📋 Copy to Clipboard
              </button>
              <button
                onClick={() => setCreatedKey(null)}
                className="btn-secondary"
              >
                ✓ I've Saved It
              </button>
            </div>
          </div>
        )}

        {/* Create Button */}
        <div style={{ marginBottom: '2rem' }}>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-success"
          >
            {showCreateForm ? '❌ Cancel' : '➕ Create New API Key'}
          </button>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <form onSubmit={handleCreateKey} className="card" style={{ marginBottom: '2rem', padding: '1.5rem', background: '#f8f9fa' }}>
            <h3 style={{ marginBottom: '1rem' }}>Create New API Key</h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                  Name *
                </label>
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production API Key"
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

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                  Rate Limit (requests/day)
                </label>
                <input
                  type="number"
                  value={newKeyRateLimit}
                  onChange={(e) => setNewKeyRateLimit(e.target.value)}
                  placeholder="e.g., 1000 (leave empty for unlimited)"
                  min="1"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    border: '2px solid var(--color-border)',
                    borderRadius: '8px',
                  }}
                />
              </div>
            </div>

            <div style={{ marginTop: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                Description
              </label>
              <textarea
                value={newKeyDescription}
                onChange={(e) => setNewKeyDescription(e.target.value)}
                placeholder="Optional description for this API key"
                rows="2"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  border: '2px solid var(--color-border)',
                  borderRadius: '8px',
                }}
              />
            </div>

            <div style={{ marginTop: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                Expiry (days from now)
              </label>
              <input
                type="number"
                value={newKeyExpiryDays}
                onChange={(e) => setNewKeyExpiryDays(e.target.value)}
                placeholder="e.g., 365 (leave empty for no expiry)"
                min="1"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  border: '2px solid var(--color-border)',
                  borderRadius: '8px',
                }}
              />
            </div>

            <button type="submit" className="btn-success" style={{ marginTop: '1rem' }}>
              🔐 Generate API Key
            </button>
          </form>
        )}

        {/* Usage Chart */}
        {Object.keys(timeline).length > 0 && <UsageChart data={timeline} />}

        {/* Search and Filter */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr',
          gap: '1rem',
          marginTop: '2rem',
          marginBottom: '1rem'
        }}>
          <input
            type="text"
            placeholder="🔍 Search by name or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: '0.75rem',
              fontSize: '1rem',
              border: '2px solid var(--color-border)',
              borderRadius: '8px',
            }}
          />

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              padding: '0.75rem',
              fontSize: '1rem',
              border: '2px solid var(--color-border)',
              borderRadius: '8px',
            }}
          >
            <option value="created_at">Sort by: Created Date</option>
            <option value="name">Sort by: Name</option>
            <option value="usage">Sort by: Usage</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={{
              padding: '0.75rem',
              fontSize: '1rem',
              border: '2px solid var(--color-border)',
              borderRadius: '8px',
            }}
          >
            <option value="all">Filter: All Keys</option>
            <option value="active">Filter: Active Only</option>
            <option value="inactive">Filter: Inactive Only</option>
            <option value="expired">Filter: Expired Only</option>
          </select>
        </div>

        <h2 style={{ marginBottom: '1rem', marginTop: '2rem' }}>
          📊 API Keys ({filteredKeys.length}{filteredKeys.length !== apiKeys.length && ` of ${apiKeys.length}`})
        </h2>

        {loading ? (
          <div className="text-center" style={{ padding: '2rem' }}>
            <p>Loading API keys...</p>
          </div>
        ) : filteredKeys.length === 0 ? (
          <div className="alert" style={{ background: '#f8f9fa' }}>
            {apiKeys.length === 0
              ? 'No API keys found. Create your first API key to get started.'
              : 'No API keys match your search or filter criteria.'}
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
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Created</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Expires</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Rate Limit</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Usage</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredKeys.map((keyData, index) => {
                  const keyPrefix = keyData.key ? keyData.key.substring(0, 8) : '';
                  const usage = usageStats[keyPrefix] || 0;
                  const status = getKeyStatus(keyData);
                  const daysUntilExpiry = calculateDaysUntilExpiry(keyData.expiry_date);

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
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span>{showKey[keyPrefix] ? keyData.key : maskKey(keyData.key)}</span>
                          <button
                            onClick={() => toggleKeyVisibility(keyPrefix)}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '1rem'
                            }}
                            title={showKey[keyPrefix] ? 'Hide key' : 'Show key'}
                          >
                            {showKey[keyPrefix] ? '🙈' : '👁️'}
                          </button>
                          <button
                            onClick={() => copyToClipboard(keyData.key)}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '1rem'
                            }}
                            title="Copy to clipboard"
                          >
                            📋
                          </button>
                        </div>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
                        {keyData.created_at ? new Date(keyData.created_at).toLocaleDateString() : 'N/A'}
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
                        {keyData.expiry_date ? (
                          <div>
                            <div>{new Date(keyData.expiry_date).toLocaleDateString()}</div>
                            {daysUntilExpiry !== null && (
                              <div style={{
                                fontSize: '0.75rem',
                                color: daysUntilExpiry < 7 ? '#dc3545' : daysUntilExpiry < 30 ? '#ffc107' : '#666'
                              }}>
                                {daysUntilExpiry > 0 ? `${daysUntilExpiry} days left` : 'Expired'}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span style={{ color: '#666' }}>Never</span>
                        )}
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
                        {keyData.rate_limit ? (
                          <div>
                            <div>{keyData.rate_limit.toLocaleString()}/day</div>
                            {keyData.daily_usage !== undefined && (
                              <div style={{ fontSize: '0.75rem', color: '#666' }}>
                                Used: {keyData.daily_usage || 0}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span style={{ color: '#666' }}>Unlimited</span>
                        )}
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center' }}>
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.85rem',
                          fontWeight: 'bold',
                          background: `${status.color}20`,
                          color: status.color,
                        }}>
                          {status.label}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                          {usage.toLocaleString()}
                        </div>
                        <button
                          onClick={() => fetchKeyLogs(keyPrefix)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#007bff',
                            cursor: 'pointer',
                            fontSize: '0.8rem',
                            textDecoration: 'underline'
                          }}
                        >
                          View Logs
                        </button>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                          <button
                            onClick={() => handleToggleKeyStatus(keyPrefix, keyData.active)}
                            className={keyData.active ? 'btn-secondary' : 'btn-success'}
                            style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                          >
                            {keyData.active ? '⏸️ Deactivate' : '▶️ Activate'}
                          </button>
                          <button
                            onClick={() => handleDeleteKey(keyPrefix, keyData.name)}
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

        {/* Usage Logs Modal */}
        {viewingLogs && selectedKeyLogs && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '2rem'
          }}>
            <div style={{
              background: 'white',
              borderRadius: '12px',
              maxWidth: '900px',
              width: '100%',
              maxHeight: '80vh',
              overflow: 'auto',
              padding: '2rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>📜 Usage Logs - {selectedKeyLogs.keyPrefix}...</h2>
                <button
                  onClick={() => setViewingLogs(false)}
                  className="btn-secondary"
                >
                  ✕ Close
                </button>
              </div>

              <p style={{ marginBottom: '1rem' }}>Total Logs: {selectedKeyLogs.count}</p>

              {selectedKeyLogs.logs.length === 0 ? (
                <div className="alert" style={{ background: '#f8f9fa' }}>
                  No usage logs found for this API key yet.
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                        <th style={{ padding: '0.75rem', textAlign: 'left' }}>Timestamp</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left' }}>IP Address</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left' }}>Method</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left' }}>Path</th>
                        <th style={{ padding: '0.75rem', textAlign: 'center' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedKeyLogs.logs.map((log, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #dee2e6' }}>
                          <td style={{ padding: '0.75rem' }}>
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>
                            {log.ip}
                          </td>
                          <td style={{ padding: '0.75rem' }}>
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              background: log.method === 'GET' ? '#e3f2fd' : '#fff3e0',
                              borderRadius: '4px',
                              fontWeight: 'bold'
                            }}>
                              {log.method}
                            </span>
                          </td>
                          <td style={{ padding: '0.75rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            {log.path}
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              background: log.http_status < 400 ? '#d4edda' : '#f8d7da',
                              color: log.http_status < 400 ? '#155724' : '#721c24',
                              borderRadius: '4px',
                              fontWeight: 'bold'
                            }}>
                              {log.http_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default APIManagement;
