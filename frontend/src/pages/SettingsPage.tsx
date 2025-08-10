import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './SettingsPage.css';

interface UserSettings {
  notifications: boolean;
  theme: 'light' | 'dark';
  privacy: 'public' | 'private';
}

const SettingsPage: React.FC = () => {
  const { token } = useAuth();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchSettings = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/settings/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else if (response.status === 404) {
        setError('Settings endpoint not found. Please check the API URL.');
      } else {
        setError('Failed to fetch settings. Please try again later.');
      }
    } catch (err) {
      setError('An error occurred while fetching settings. Please check your network connection.');
    }
  }, [token]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    setSettings(prev => prev ? { ...prev, [name]: type === 'checkbox' ? checked : value } : null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (!settings) {
      setError('Settings are not loaded yet.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/settings/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        setSuccess('Settings updated successfully!');
        const updatedSettings = await response.json();
        setSettings(updatedSettings); // Update UI with the latest settings
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to update settings');
      }
    } catch (err) {
      setError('An error occurred while updating settings');
    } finally {
      setLoading(false);
    }
  };

  if (!settings) {
    return <div className="settings-container">Loading settings...</div>;
  }

  return (
    <div className="settings-container">
      <h2>Settings</h2>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <form onSubmit={handleSubmit} className="settings-form">
        <div className="form-group">
          <label htmlFor="notifications">Enable Notifications</label>
          <input
            type="checkbox"
            id="notifications"
            name="notifications"
            checked={settings.notifications}
            onChange={handleInputChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="theme">Theme</label>
          <select
            id="theme"
            name="theme"
            value={settings.theme}
            onChange={handleInputChange}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="privacy">Account Privacy</label>
          <select
            id="privacy"
            name="privacy"
            value={settings.privacy}
            onChange={handleInputChange}
          >
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="save-button">
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SettingsPage;
