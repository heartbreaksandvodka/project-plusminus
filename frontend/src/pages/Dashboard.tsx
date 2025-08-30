
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';
import { statisticsService, AccountStatistics } from '../services/api/statistics';
import { manualStatisticsService, ManualStatistics } from '../services/api/manualStatistics';
import MT5AccountCard from '../components/MT5AccountCard';
import EAGraphs from '../components/EAGraphs/EAGraphs';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [accountStats, setAccountStats] = useState<AccountStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [manualStats, setManualStats] = useState<ManualStatistics | null>(null);
  const { user } = useAuth();
  const { settings } = useSettings();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Single API call to get ALL statistics (EA + Manual)
        const stats = await statisticsService.getAccountStatistics();
        setAccountStats(stats);
        // Extract manual stats from the comprehensive response
        setManualStats(stats.manual_stats);
      } catch (error) {
        setAccountStats(null);
        setManualStats(null);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
    // Poll every 30s for live stats
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };



  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }




  // Use backend-calculated values directly (no frontend recalculation needed)
  const manualProfitability = manualStats?.profitability_percent 
    ? `${manualStats.profitability_percent}%` 
    : '0%';

  return (
    <div className="dashboard-container">
      <main className="dashboard-content">

        {/* EA Statistics - Show based on user setting */}
        {settings?.show_ea_statistics && (
          <div className="dashboard-card">
            <h2>📊 EA Statistics</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{accountStats?.ea_activity.length}</div>
                <div className="stat-label">Active EAs</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{accountStats?.running_eas}</div>
                <div className="stat-label">Running EAs</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{accountStats?.ea_profitability_percent}%</div>
                <div className="stat-label">EA Profitability</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{accountStats?.ea_total_trades}</div>
                <div className="stat-label">EA Trades</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{accountStats?.ea_win_rate}%</div>
                <div className="stat-label">EA Win Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* EA Activity - Show based on user setting */}
        {settings?.show_ea_statistics && (
          <div className="dashboard-card">
            <h2>⚡ EA Activity</h2>
            {accountStats?.ea_activity && accountStats.ea_activity.length > 0 ? (
              <ul className="ea-activity-list">
                {accountStats.ea_activity.map((ea, idx) => (
                  <li key={idx} className="ea-activity-item">
                    <span className="ea-name">{ea.ea_name}</span>
                    <div className="ea-duration">Duration: {ea.active_duration}</div>
                    <div className="ea-start-time">Started: {new Date(ea.start_time).toLocaleString()}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">🤖</div>
                <h4>No Active EAs</h4>
                <p>Your Expert Advisors are currently not running</p>
              </div>
            )}
          </div>
        )}

        {/* Manual Trading Statistics - Show based on user setting */}
        {settings?.show_ea_statistics && (
          <div className="dashboard-card">
            <h2>📝 Manual Trading Statistics</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{manualStats?.total_trades}</div>
                <div className="stat-label">Manual Trades</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{manualProfitability}</div>
                <div className="stat-label">Manual Profitability</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{manualStats?.win_rate}%</div>
                <div className="stat-label">Manual Win Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* Manual Trading Sessions - Show based on user setting */}
        {settings?.show_ea_statistics && (
          <div className="dashboard-card">
            <h2>📝 Manual Trading Sessions</h2>
            {manualStats?.sessions && manualStats.sessions.length > 0 ? (
              <ul className="trading-sessions-list">
                {manualStats.sessions.slice(0, 3).map((session, idx) => (
                  <li key={idx} className="trading-session-item">
                    <div className="session-header">
                      <span className="session-label">Trading Session #{idx + 1}</span>
                      <span className={`session-status ${session.session_end ? 'completed' : 'ongoing'}`}>
                        {session.session_end ? 'Completed' : 'Ongoing'}
                      </span>
                    </div>
                    <div className="session-timeframe">
                      <strong>Time:</strong> {new Date(session.session_start).toLocaleString()} 
                      {session.session_end && (
                        <> - {new Date(session.session_end).toLocaleString()}</>
                      )}
                    </div>
                    <div className="session-metrics">
                      <div className="session-metric">
                        <span className="metric-label">Trades:</span>
                        <span className="metric-value">{session.trades_executed}</span>
                      </div>
                      <div className="session-metric">
                        <span className="metric-label">P/L:</span>
                        <span className={`metric-value ${
                          session.profit_loss >= 0 ? 'positive' : 'negative'
                        }`}>
                          {session.profit_loss}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <h4>No Manual Trading Sessions</h4>
                <p>You haven't recorded any manual trading sessions yet</p>
              </div>
            )}
          </div>
        )}

        {/* Charts Section - Show when EA statistics are enabled */}
        {settings?.show_ea_statistics && (
          <div className="dashboard-card charts-card">
            <h2>📈 Trading Analytics & Charts</h2>
            <EAGraphs accountStats={accountStats} manualStats={manualStats} />
          </div>
        )}

        {/* Show message when EA statistics are hidden */}
        {settings?.show_ea_statistics === false && (
          <div className="dashboard-card">
            <h2>📊 Account Statistics</h2>
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#666' }}>
              <div style={{ fontSize: '3rem', marginBottom: '20px' }}>👁️‍🗨️</div>
              <h3 style={{ color: '#333', marginBottom: '10px' }}>EA Statistics Hidden</h3>
              <p>EA activity statistics are currently hidden.</p>
              <button 
                onClick={() => navigate('/settings')}
                style={{
                  marginTop: '15px',
                  padding: '10px 20px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
              >
                Show in Settings
              </button>
            </div>
          </div>
        )}

        {/* User Information */}
        <div className="dashboard-card">
          <h2>👤 User Information</h2>
          <div className="user-info">
            <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Member since:</strong> {new Date(user?.date_joined || '').toLocaleDateString()}</p>
            {user?.last_login && (
              <p><strong>Last login:</strong> {formatDate(user.last_login)}</p>
            )}
          </div>
        </div>

        {/* MT5 Account Integration */}
        <MT5AccountCard />

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
        {/* No recent_activity data available, block removed or implement if data source is added */}

        {/* Notifications */}
        {/* No notifications data available, block removed or implement if data source is added */}

        {/* Welcome Message */}
        <div className="dashboard-card">
          <h2>💬 Welcome Message</h2>
          <p style={{ fontSize: '1.1rem', color: '#555', lineHeight: '1.6' }}>
            {'Welcome to your dashboard!'}
          </p>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
