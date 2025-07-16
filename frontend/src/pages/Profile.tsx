import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Profile.css';

const Profile: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>👤 My Profile</h1>
        <p>View and manage your account information</p>
      </div>

      <div className="profile-content">
        {/* Profile Card */}
        <div className="profile-card">
          <div className="profile-avatar">
            <span className="avatar-text">
              {user?.first_name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="profile-info">
            <h2>{user?.first_name} {user?.last_name}</h2>
            <p className="profile-email">{user?.email}</p>
            <p className="profile-username">@{user?.username}</p>
          </div>
        </div>

        {/* Profile Details */}
        <div className="profile-details">
          <h3>Account Details</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>First Name</label>
              <span>{user?.first_name || 'Not specified'}</span>
            </div>
            <div className="detail-item">
              <label>Last Name</label>
              <span>{user?.last_name || 'Not specified'}</span>
            </div>
            <div className="detail-item">
              <label>Email</label>
              <span>{user?.email}</span>
            </div>
            <div className="detail-item">
              <label>Username</label>
              <span>{user?.username}</span>
            </div>
            <div className="detail-item">
              <label>Member Since</label>
              <span>{new Date(user?.date_joined || '').toLocaleDateString()}</span>
            </div>
            <div className="detail-item">
              <label>Account Status</label>
              <span className="status-active">Active</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="profile-actions">
          <h3>Quick Actions</h3>
          <div className="action-buttons">
            <button className="action-btn primary">
              📝 Edit Profile
            </button>
            <button className="action-btn secondary">
              🔒 Change Password
            </button>
            <button className="action-btn secondary">
              🔔 Notification Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
