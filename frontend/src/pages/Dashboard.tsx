import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services';
import './Dashboard.css';

interface DashboardData {
  message: string;
  user: any;
  stats: {
    account_age_days: number;
    profile_completeness: number;
    total_logins: number;
    last_login: string | null;
  };
  recent_activity: Array<{
    action: string;
    timestamp: string;
    description: string;
  }>;
  notifications: Array<{
    type: string;
    message: string;
    timestamp: string;
  }>;
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await authService.getDashboard();
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'info': return 'ℹ️';
      case 'warning': return '⚠️';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <main className="dashboard-content">
        {/* User Statistics */}
        <div className="dashboard-card">
          <h2>📊 Account Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{dashboardData?.stats.account_age_days || 0}</div>
              <div className="stat-label">Days Active</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{dashboardData?.stats.profile_completeness || 0}%</div>
              <div className="stat-label">Profile Complete</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{dashboardData?.stats.total_logins || 0}</div>
              <div className="stat-label">Total Logins</div>
            </div>
          </div>
          <div style={{ marginTop: '20px' }}>
            <p><strong>Profile Completeness:</strong></p>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${dashboardData?.stats.profile_completeness || 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* User Information */}
        <div className="dashboard-card">
          <h2>👤 User Information</h2>
          <div className="user-info">
            <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Member since:</strong> {new Date(user?.date_joined || '').toLocaleDateString()}</p>
            {dashboardData?.stats.last_login && (
              <p><strong>Last login:</strong> {formatDate(dashboardData.stats.last_login)}</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-card">
          <h2>⚡ Quick Actions</h2>
          <div className="quick-actions">
            <button onClick={() => navigate('/update-profile')} className="action-button">
              📝 Update Profile
            </button>
            <button onClick={() => navigate('/change-password')} className="action-button">
              🔒 Change Password
            </button>
            <button onClick={() => navigate('/subscriptions')} className="action-button">
              💳 View Subscriptions
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card">
          <h2>📈 Recent Activity</h2>
          <div className="activity-list">
            {dashboardData?.recent_activity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-info">
                  <div className="activity-action">{activity.action}</div>
                  <div className="activity-description">{activity.description}</div>
                </div>
                <div className="activity-time">
                  {formatDate(activity.timestamp)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Notifications */}
        <div className="dashboard-card">
          <h2>🔔 Notifications</h2>
          <div className="notifications-list">
            {dashboardData?.notifications.map((notification, index) => (
              <div key={index} className={`notification-item ${notification.type}`}>
                <div className="notification-icon">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="notification-content">
                  <div className="notification-message">{notification.message}</div>
                  <div className="notification-time">
                    {formatDate(notification.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Welcome Message */}
        <div className="dashboard-card">
          <h2>💬 Welcome Message</h2>
          <p style={{ fontSize: '1.1rem', color: '#555', lineHeight: '1.6' }}>
            {dashboardData?.message || 'Welcome to your dashboard!'}
          </p>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
