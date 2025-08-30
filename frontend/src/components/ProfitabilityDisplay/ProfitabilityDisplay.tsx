import React, { useMemo } from 'react';
import { ProfitabilityCalculator, ProfitabilityData } from '../../utils/profitabilityCalculator';
import './ProfitabilityDisplay.css';

interface ProfitabilityDisplayProps {
  accountStats: any;
  realTimeData?: {
    current_balance: number;
    unrealized_pnl: number;
    open_positions: number;
  };
  showDetailed?: boolean;
  className?: string;
}

const ProfitabilityDisplay: React.FC<ProfitabilityDisplayProps> = ({
  accountStats,
  realTimeData,
  showDetailed = false,
  className
}) => {

  // Calculate comprehensive profitability metrics
  const profitabilityMetrics = useMemo(() => {
    // Mock data structure - replace with real data from your API
    const profitabilityData: ProfitabilityData = {
      initial_balance: 10000, // This should come from user's account
      current_balance: realTimeData?.current_balance || 10000,
      realized_pnl: accountStats?.total_profit || 0,
      unrealized_pnl: realTimeData?.unrealized_pnl || 0,
      total_deposits: 0, // Add to your API
      total_withdrawals: 0, // Add to your API
      total_trades: accountStats?.total_trades || 0,
      winning_trades: Math.round((accountStats?.total_trades || 0) * (accountStats?.win_rate || 0) / 100),
      losing_trades: (accountStats?.total_trades || 0) - Math.round((accountStats?.total_trades || 0) * (accountStats?.win_rate || 0) / 100),
      total_profit: accountStats?.total_profit || 0,
      total_loss: accountStats?.total_loss || 0,
      max_drawdown: accountStats?.max_drawdown || 0,
      max_consecutive_losses: accountStats?.max_consecutive_losses || 0,
      trading_days: accountStats?.trading_days || 30,
      start_date: accountStats?.start_date || new Date().toISOString(),
    };

    return ProfitabilityCalculator.calculateProfitability(profitabilityData);
  }, [accountStats, realTimeData]);

  const getProfitabilityStatus = (value: number): string => {
    if (value > 15) return 'excellent';
    if (value > 5) return 'good';
    if (value > 0) return 'positive';
    if (value === 0) return 'neutral';
    if (value > -10) return 'warning';
    return 'loss';
  };

  const profitabilityStatus = getProfitabilityStatus(profitabilityMetrics.total_profitability);

  if (!showDetailed) {
    // Simple display for dashboard cards
    return (
      <div className={`profitability-simple ${className || ''}`}>
        <div 
          className="profitability-value"
          style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.total_profitability) }}
        >
          {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.total_profitability)}
        </div>
        {realTimeData?.unrealized_pnl !== 0 && (
          <div className="unrealized-indicator">
            <span className="unrealized-label">Unrealized:</span>
            <span 
              className="unrealized-value"
              style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.unrealized_profitability) }}
            >
              {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.unrealized_profitability)}
            </span>
          </div>
        )}
      </div>
    );
  }

  // Detailed profitability display
  return (
    <div className={`profitability-detailed ${className || ''}`}>
      <div className="profitability-header">
        <h3>💰 Profitability Analysis</h3>
        <div className={`profitability-status ${profitabilityStatus}`}>
          {profitabilityStatus.toUpperCase()}
        </div>
      </div>

      <div className="profitability-grid">
        {/* Main Profitability */}
        <div className="profitability-card main">
          <div className="card-header">
            <div className="card-icon">📈</div>
            <div className="card-title">Total Profitability</div>
          </div>
          <div 
            className="card-value large"
            style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.total_profitability) }}
          >
            {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.total_profitability)}
          </div>
          <div className="card-breakdown">
            <div className="breakdown-item">
              <span>Realized:</span>
              <span style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.realized_profitability) }}>
                {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.realized_profitability)}
              </span>
            </div>
            <div className="breakdown-item">
              <span>Unrealized:</span>
              <span style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.unrealized_profitability) }}>
                {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.unrealized_profitability)}
              </span>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="profitability-card">
          <div className="card-header">
            <div className="card-icon">🎯</div>
            <div className="card-title">Win Rate</div>
          </div>
          <div className="card-value">
            {profitabilityMetrics.win_rate}%
          </div>
          <div className="card-subtitle">
            {profitabilityMetrics.win_rate > 60 ? 'Excellent' : 
             profitabilityMetrics.win_rate > 50 ? 'Good' : 'Needs Improvement'}
          </div>
        </div>

        {/* Profit Factor */}
        <div className="profitability-card">
          <div className="card-header">
            <div className="card-icon">⚖️</div>
            <div className="card-title">Profit Factor</div>
          </div>
          <div className="card-value">
            {profitabilityMetrics.profit_factor === Infinity ? '∞' : profitabilityMetrics.profit_factor}
          </div>
          <div className="card-subtitle">
            {profitabilityMetrics.profit_factor > 2 ? 'Excellent' : 
             profitabilityMetrics.profit_factor > 1.2 ? 'Good' : 'Poor'}
          </div>
        </div>

        {/* Daily Average */}
        <div className="profitability-card">
          <div className="card-header">
            <div className="card-icon">📅</div>
            <div className="card-title">Daily Average</div>
          </div>
          <div 
            className="card-value"
            style={{ color: ProfitabilityCalculator.getProfitabilityColor(profitabilityMetrics.daily_average) }}
          >
            {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.daily_average)}
          </div>
          <div className="card-subtitle">
            Per trading day
          </div>
        </div>

        {/* Sharpe Ratio */}
        <div className="profitability-card">
          <div className="card-header">
            <div className="card-icon">📊</div>
            <div className="card-title">Sharpe Ratio</div>
          </div>
          <div className="card-value">
            {profitabilityMetrics.sharpe_ratio}
          </div>
          <div className="card-subtitle">
            Risk-adjusted returns
          </div>
        </div>

        {/* Max Drawdown */}
        <div className="profitability-card">
          <div className="card-header">
            <div className="card-icon">⬇️</div>
            <div className="card-title">Max Drawdown</div>
          </div>
          <div 
            className="card-value"
            style={{ color: profitabilityMetrics.max_drawdown_percent > 20 ? '#ef4444' : '#f59e0b' }}
          >
            {ProfitabilityCalculator.formatProfitability(profitabilityMetrics.max_drawdown_percent)}
          </div>
          <div className="card-subtitle">
            Maximum loss from peak
          </div>
        </div>
      </div>

      {/* Real-time Update Indicator */}
      {realTimeData && (
        <div className="real-time-update">
          <div className="update-indicator">
            <div className="pulse-dot"></div>
            <span>Live profitability • {realTimeData.open_positions} open positions</span>
          </div>
          <div className="last-updated">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfitabilityDisplay;
