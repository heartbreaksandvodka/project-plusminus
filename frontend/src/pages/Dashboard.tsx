
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { statisticsService, AccountStatistics } from '../services/api/statistics';
import { manualStatisticsService, ManualStatistics } from '../services/api/manualStatistics';
import MT5AccountCard from '../components/MT5AccountCard';
import './Dashboard.css';

// Helper to format percentages to 1 decimal and max 3 significant digits (e.g., -22.4%)
const formatPercent = (value: number | string | undefined | null) => {
  if (value === undefined || value === null || value === '') return '0%';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0%';
  // Clamp to -99.9% to 99.9% for display, show '>99.9%' or '<-99.9%' for out-of-range
  if (num > 99.9) return '>99.9%';
  if (num < -99.9) return '<-99.9%';
  return `${num.toFixed(1)}%`;
};

const Dashboard: React.FC = () => {
  const [accountStats, setAccountStats] = useState<AccountStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [manualStats, setManualStats] = useState<ManualStatistics | null>(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const stats = await statisticsService.getAccountStatistics();
        setAccountStats(stats);
      } catch (error) {
        setAccountStats(null);
      }
      try {
        const manual = await manualStatisticsService.getManualStatistics();
        setManualStats(manual);
      } catch (error) {
        setManualStats(null);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
    // Optionally, poll every 30s for live stats
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
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



  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }




  // Custom manual profitability calculation: profit/loss ratio as a percentage
  let customManualProfitability: string = '0%';
  let trades: any[] = [];
  if (manualStats && Array.isArray((manualStats as any).trades)) {
    trades = (manualStats as any).trades;
  } else if (manualStats && Array.isArray((manualStats as any).sessions)) {
    // Try to extract trades from sessions if present
    trades = (manualStats as any).sessions.flatMap((s: any) => Array.isArray(s.trades) ? s.trades : []);
  }
  if (trades.length > 0) {
    const profits = trades.filter((t: any) => typeof t.profit === 'number' && t.profit > 0).map((t: any) => t.profit);
    const losses = trades.filter((t: any) => typeof t.profit === 'number' && t.profit < 0).map((t: any) => t.profit);
    const sumProfits = profits.reduce((a: number, b: number) => a + b, 0);
    const sumLosses = losses.reduce((a: number, b: number) => a + b, 0);
    if (sumLosses !== 0) {
      const ratio = (sumProfits / Math.abs(sumLosses)) * 100;
      customManualProfitability = formatPercent(ratio);
    } else if (sumProfits > 0) {
      customManualProfitability = '100%';
    } else {
      customManualProfitability = '0%';
    }
  }

  return (
    <div className="dashboard-container">
      <main className="dashboard-content">

        {/* Account Statistics (Live) */}
        <div className="dashboard-card">
          <h2>📊 Account Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{accountStats?.ea_activity.length || 0}</div>
              <div className="stat-label">Active EAs</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{accountStats?.running_eas || 0}</div>
              <div className="stat-label">Running EAs</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{formatPercent(accountStats?.profitability_percent)}</div>
              <div className="stat-label">Profitability</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{accountStats?.total_trades || 0}</div>
              <div className="stat-label">Total Trades</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{formatPercent(accountStats?.win_rate)}</div>
              <div className="stat-label">Win Rate</div>
            </div>
          </div>
          <div style={{ marginTop: '20px' }}>
            <p><strong>EA Activity:</strong></p>
            <ul>
              {accountStats?.ea_activity.map((ea, idx) => (
                <li key={idx}>
                  <strong>{ea.ea_name}</strong>: {ea.active_duration} (Started: {new Date(ea.start_time).toLocaleString()})
                </li>
              ))}
            </ul>
          </div>

          {/* Manual/Non-EA Account Statistics (Live) */}
          <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
            <h3>📝 Manual/Non-EA Account Statistics (Live)</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{manualStats?.total_trades || 0}</div>
                <div className="stat-label">Manual Trades</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{customManualProfitability}</div>
                <div className="stat-label">Manual Profitability</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{formatPercent(manualStats?.win_rate)}</div>
                <div className="stat-label">Manual Win Rate</div>
              </div>
            </div>
            <div style={{ marginTop: '20px' }}>
              <p><strong>Manual Trading Sessions:</strong></p>
              <ul>
                {manualStats?.sessions.slice(0, 3).map((session, idx) => (
                  <li key={idx}>
                    <strong>Session:</strong> {new Date(session.session_start).toLocaleString()} - {session.session_end ? new Date(session.session_end).toLocaleString() : 'Ongoing'}<br />
                    <strong>Trades:</strong> {session.trades_executed} | <strong>P/L:</strong> {session.profit_loss}
                  </li>
                ))}
              </ul>
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
