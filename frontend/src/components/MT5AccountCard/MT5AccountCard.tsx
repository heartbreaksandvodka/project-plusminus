import React, { useState, useEffect } from 'react';
import { mt5Service } from '../../services/api';
import { MT5Account, MT5AccountForm } from '../../types/mt5';
import './MT5AccountCard.css';

const MT5AccountCard: React.FC = () => {
  const [account, setAccount] = useState<MT5Account | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState<MT5AccountForm>({
    account_number: '',
    broker_name: '',
    server: '',
    password: '',
    account_type: 'demo'
  });

  useEffect(() => {
    loadAccount();
  }, []);

  const loadAccount = async () => {
    try {
      setLoading(true);
      setError('');
      const accountData = await mt5Service.getAccount();
      setAccount(accountData);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // No account found, show form
        setShowForm(true);
      } else {
        setError('Failed to load MT5 account');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const result = await mt5Service.saveAccount(formData);
      setAccount(result.account);
      setShowForm(false);
      setSuccess('MT5 account saved successfully!');
      
      // Clear form
      setFormData({
        account_number: '',
        broker_name: '',
        server: '',
        password: '',
        account_type: 'demo'
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save MT5 account');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!formData.account_number || !formData.password || !formData.server) {
      setError('Please fill in all required fields');
      return;
    }

    setTesting(true);
    setError('');
    setSuccess('');

    try {
      const result = await mt5Service.testConnection(formData);
      if (result.status === 'success') {
        setSuccess('Connection test successful!');
      } else {
        setError(result.error?.error || 'Connection test failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.error || 'Connection test failed');
    } finally {
      setTesting(false);
    }
  };

  const handleRefreshStatus = async () => {
    if (!account) return;

    setRefreshing(true);
    setError('');

    try {
      const result = await mt5Service.refreshStatus();
      setAccount(result.account);
      setSuccess('Account status refreshed!');
    } catch (err: any) {
      setError('Failed to refresh account status');
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure you want to delete your MT5 account? This action cannot be undone.')) {
      return;
    }

    try {
      await mt5Service.deleteAccount();
      setAccount(null);
      setShowForm(true);
      setSuccess('MT5 account deleted successfully');
    } catch (err: any) {
      setError('Failed to delete MT5 account');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return '#28a745';
      case 'disconnected': return '#6c757d';
      case 'error': return '#dc3545';
      case 'pending': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return '🟢';
      case 'disconnected': return '⚪';
      case 'error': return '🔴';
      case 'pending': return '🟡';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="mt5-card">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading MT5 account...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt5-card">
      <div className="mt5-card-header">
        <h3>
          <span className="mt5-icon">📈</span>
          MetaTrader 5 Account
        </h3>
        {account && (
          <div className="header-actions">
            <button
              className="btn-refresh"
              onClick={handleRefreshStatus}
              disabled={refreshing}
              title="Refresh Status"
            >
              {refreshing ? '⏳' : '🔄'}
            </button>
            <button
              className="btn-edit"
              onClick={() => setShowForm(!showForm)}
              title="Edit Account"
            >
              ⚙️
            </button>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {!account && !showForm ? (
        <div className="no-account-state">
          <div className="empty-icon">🔌</div>
          <h4>No MT5 Account Connected</h4>
          <p>Connect your MetaTrader 5 account to run trading algorithms</p>
          <button 
            className="btn-primary"
            onClick={() => setShowForm(true)}
          >
            Connect MT5 Account
          </button>
        </div>
      ) : null}

      {account && !showForm ? (
        <div className="account-display">
          <div className="account-status">
            <div className="status-indicator">
              <span className="status-icon">{getStatusIcon(account.connection_status)}</span>
              <span 
                className="status-text"
                style={{ color: getStatusColor(account.connection_status) }}
              >
                {account.connection_status.charAt(0).toUpperCase() + account.connection_status.slice(1)}
              </span>
            </div>
            {account.last_connected && (
              <div className="last-connected">
                Last connected: {new Date(account.last_connected).toLocaleString()}
              </div>
            )}
          </div>

          <div className="account-details">
            <div className="detail-row">
              <span className="label">Account:</span>
              <span className="value">{account.masked_account_number}</span>
            </div>
            <div className="detail-row">
              <span className="label">Broker:</span>
              <span className="value">{account.broker_name}</span>
            </div>
            <div className="detail-row">
              <span className="label">Type:</span>
              <span className={`badge ${account.account_type}`}>
                {account.account_type.toUpperCase()}
              </span>
            </div>
          </div>

          {account.is_connected && (
            <div className="account-balance">
              <div className="balance-item">
                <span className="balance-label">Balance:</span>
                <span className="balance-value">
                  {account.balance ? `${account.balance.toFixed(2)} ${account.currency}` : 'N/A'}
                </span>
              </div>
              <div className="balance-item">
                <span className="balance-label">Equity:</span>
                <span className="balance-value">
                  {account.equity ? `${account.equity.toFixed(2)} ${account.currency}` : 'N/A'}
                </span>
              </div>
              <div className="balance-item">
                <span className="balance-label">Margin:</span>
                <span className="balance-value">
                  {account.margin ? `${account.margin.toFixed(2)} ${account.currency}` : 'N/A'}
                </span>
              </div>
            </div>
          )}

          <div className="account-actions">
            <button 
              className="btn-secondary"
              onClick={() => setShowForm(true)}
            >
              Edit Account
            </button>
            <button 
              className="btn-danger"
              onClick={handleDeleteAccount}
            >
              Delete Account
            </button>
          </div>
        </div>
      ) : null}

      {showForm && (
        <div className="account-form">
          <h4>{account ? 'Edit MT5 Account' : 'Add MT5 Account'}</h4>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="account_number">Account Number *</label>
              <input
                type="text"
                id="account_number"
                name="account_number"
                value={formData.account_number}
                onChange={handleChange}
                required
                placeholder="Enter your MT5 account number"
              />
            </div>

            <div className="form-group">
              <label htmlFor="broker_name">Broker Name *</label>
              <input
                type="text"
                id="broker_name"
                name="broker_name"
                value={formData.broker_name}
                onChange={handleChange}
                required
                placeholder="e.g., XM, FXCM, IG"
              />
            </div>

            <div className="form-group">
              <label htmlFor="server">Server *</label>
              <input
                type="text"
                id="server"
                name="server"
                value={formData.server}
                onChange={handleChange}
                required
                placeholder="e.g., XM-Real, XM-Demo"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <div className="password-input-container">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="Enter your MT5 password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "👁️" : "🙈"}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="account_type">Account Type</label>
              <select
                id="account_type"
                name="account_type"
                value={formData.account_type}
                onChange={handleChange}
              >
                <option value="demo">Demo Account</option>
                <option value="real">Real Account</option>
              </select>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn-test"
                onClick={handleTestConnection}
                disabled={testing}
              >
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Account'}
              </button>
              {account && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default MT5AccountCard;
