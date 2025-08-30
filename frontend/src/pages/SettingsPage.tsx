import React, { useState } from 'react';
import { useSettings } from '../contexts/SettingsContext';
import './SettingsPage.css';

const SettingsPage: React.FC = () => {
  const { settings, loading, updateSettings } = useSettings();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!settings) {
    return <div className="settings-container">Loading settings...</div>;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    
    // Update settings immediately for better UX
    const newValue = type === 'checkbox' ? checked : value;
    handleSettingUpdate(name, newValue);
  };

  const handleSettingUpdate = async (field: string, value: any) => {
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      await updateSettings({ [field]: value });
      setSuccess('Setting updated successfully!');
      setTimeout(() => setSuccess(''), 3000); // Clear success message after 3 seconds
    } catch (err) {
      setError('Failed to update setting. Please try again.');
      setTimeout(() => setError(''), 5000); // Clear error message after 5 seconds
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="settings-container">
      <h2>⚙️ Settings</h2>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="settings-form">
        <div className="form-group">
          <label htmlFor="notifications">
            <span className="toggle-label">Enable Notifications</span>
            <span className="toggle-description">
              Receive email and app notifications about your account activity
            </span>
          </label>
          <div className="toggle-switch">
            <input
              type="checkbox"
              id="notifications"
              name="notifications"
              checked={settings.notifications}
              onChange={handleInputChange}
              className="toggle-input"
              disabled={isSaving}
            />
            <label htmlFor="notifications" className="toggle-slider">
              <span className="toggle-button"></span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="show_ea_statistics">
            <span className="toggle-label">Show EA Activity Statistics on Dashboard</span>
            <span className="toggle-description">
              Display detailed EA performance metrics and activity data on your dashboard
            </span>
          </label>
          <div className="toggle-switch">
            <input
              type="checkbox"
              id="show_ea_statistics"
              name="show_ea_statistics"
              checked={settings.show_ea_statistics}
              onChange={handleInputChange}
              className="toggle-input"
              disabled={isSaving}
            />
            <label htmlFor="show_ea_statistics" className="toggle-slider">
              <span className="toggle-button"></span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="privacy">
            <span className="toggle-label">Account Privacy</span>
            <span className="toggle-description">
              Control who can see your trading performance and activity
            </span>
          </label>
          <select
            id="privacy"
            name="privacy"
            value={settings.privacy}
            onChange={handleInputChange}
            disabled={isSaving}
          >
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>

        {isSaving && (
          <div className="saving-indicator">
            <div className="saving-spinner"></div>
            <span>Saving...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;
