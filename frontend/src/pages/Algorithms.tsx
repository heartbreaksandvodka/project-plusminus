import React, { useState, useEffect } from 'react';
import './Algorithms.css';
import { FloatingSupportWidget } from '../components/Support';
import algorithmsService, { Algorithm, AlgorithmExecution } from '../services/api/algorithms';
import { getUserSubscription } from '../services/api/subscriptions';
import { getMT5Accounts } from '../services/api/mt5';

const Algorithms: React.FC = () => {
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [userSubscription, setUserSubscription] = useState<any>(null);
  const [mt5Accounts, setMT5Accounts] = useState<any[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  
  // Risk Management States
  const [showRiskManager, setShowRiskManager] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        await Promise.all([
          loadAlgorithms(),
          loadSubscription(),
          loadMT5Accounts()
        ]);
      } catch (err) {
        console.error('Error loading data:', err);
      }
    };

    loadInitialData();
  }, []);

  const loadAlgorithms = async () => {
    try {
      const availableAlgorithms = await algorithmsService.getAvailableAlgorithms();
      setAlgorithms(availableAlgorithms);
    } catch (err) {
      console.error('Failed to load algorithms:', err);
    }
  };

  const loadSubscription = async () => {
    try {
      const subscription = await getUserSubscription();
      setUserSubscription(subscription);
    } catch (err) {
      console.error('Failed to load subscription:', err);
      // Fallback to mock data for demo purposes
      setUserSubscription({
        id: 1,
        plan_type: 'pro',
        max_algorithms: 10,
        max_mt5_accounts: 2,
        status: 'active',
        start_date: '2025-01-01',
        auto_renew: true,
        features: ['All algorithms', 'Risk management', 'Multiple accounts']
      });
    }
  };

  const loadMT5Accounts = async () => {
    try {
      const accounts = await getMT5Accounts();
      setMT5Accounts(accounts);
      if (accounts.length > 0 && !selectedAccount) {
        setSelectedAccount(accounts[0].id.toString());
      }
    } catch (err) {
      console.error('Failed to load MT5 accounts:', err);
      // Fallback to mock data for demo purposes
      setMT5Accounts([
        { id: '1', account_number: '12345678', broker: 'Exness', status: 'connected' },
        { id: '2', account_number: '87654321', broker: 'IC Markets', status: 'connected' }
      ]);
      if (!selectedAccount) {
        setSelectedAccount('1');
      }
    }
  };
  
  const getAvailableAlgorithms = () => {
    if (!userSubscription) return algorithms.slice(0, 2); // Basic plan
    
    switch (userSubscription.plan_type) {
      case 'basic': return algorithms.slice(0, 2);
      case 'premium': return algorithms.slice(0, 5);
      case 'pro': return algorithms;
      case 'enterprise': return algorithms;
      default: return algorithms.slice(0, 2);
    }
  };

  // Risk Management Functions
  const updateRiskManagement = (algorithmId: string, riskSettings: Partial<Algorithm['riskManagement']>) => {
    setAlgorithms(prev => prev.map(algo => 
      algo.id === algorithmId 
        ? { ...algo, riskManagement: { ...algo.riskManagement, ...riskSettings } }
        : algo
    ));
  };

  const validateRiskSettings = (settings: Algorithm['riskManagement']): string[] => {
    const errors: string[] = [];
    if (settings.maxLossPerTrade > 10) errors.push('Max loss per trade should not exceed 10%');
    if (settings.maxDailyLoss > 20) errors.push('Max daily loss should not exceed 20%');
    if (settings.positionSize > 5) errors.push('Position size should not exceed 5%');
    if (settings.stopLoss > settings.takeProfit) errors.push('Stop loss should be less than take profit');
    return errors;
  };

  const handleDeploy = (algorithmId: string, symbol: string) => {
    if (!selectedAccount) {
      alert('Please select an MT5 account first');
      return;
    }
    
    const algorithm = algorithms.find(algo => algo.id === algorithmId);
    if (algorithm) {
      const riskErrors = validateRiskSettings(algorithm.riskManagement);
      if (riskErrors.length > 0) {
        alert('Risk management errors: ' + riskErrors.join(', '));
        return;
      }
    }
    
    setAlgorithms(prev => prev.map(algo => 
      algo.id === algorithmId 
        ? { ...algo, isDeployed: true, selectedSymbol: symbol }
        : algo
    ));
    
    // TODO: Send deploy command to MT5 service
    console.log(`Deploying algorithm ${algorithmId} on ${symbol} with account ${selectedAccount}`);
  };

  const handlePause = (algorithmId: string) => {
    setAlgorithms(prev => prev.map(algo => 
      algo.id === algorithmId 
        ? { ...algo, isPaused: !algo.isPaused }
        : algo
    ));
    
    // TODO: Send pause/resume command to MT5 service
  };

  const handleStop = (algorithmId: string) => {
    setAlgorithms(prev => prev.map(algo => 
      algo.id === algorithmId 
        ? { ...algo, isDeployed: false, isPaused: false, selectedSymbol: '' }
        : algo
    ));
    
    // TODO: Send stop command to MT5 service
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return '#10b981';
      case 'Medium': return '#f59e0b';
      case 'High': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'forex': return '💱';
      case 'stocks': return '📈';
      case 'crypto': return '₿';
      case 'indices': return '📊';
      default: return '🤖';
    }
  };

  return (
    <div className="algorithms-page">
      <div className="algorithms-header">
        <h1>Trading Algorithms</h1>
        <p>Deploy and manage your automated trading strategies</p>
        
        <div className="account-selector">
          <label htmlFor="mt5-account">Select MT5 Account:</label>
          <select 
            id="mt5-account"
            value={selectedAccount} 
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="account-select"
          >
            <option value="">Choose MT5 Account</option>
            {mt5Accounts.map(account => (
              <option key={account.id} value={account.id}>
                {account.account_number} - {account.broker}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="algorithms-grid">
        {getAvailableAlgorithms().map(algorithm => (
          <div key={algorithm.id} className={`algorithm-card ${!algorithm.isActive ? 'locked' : ''}`}>
            <div className="algorithm-header">
              <div className="algorithm-info">
                <h3>
                  {getCategoryIcon(algorithm.category)} {algorithm.name}
                  {algorithm.isDeployed && <span className="deployed-badge">Live</span>}
                  {algorithm.isPaused && <span className="paused-badge">Paused</span>}
                </h3>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(algorithm.riskLevel) }}
                >
                  {algorithm.riskLevel} Risk
                </span>
              </div>
              {algorithm.isActive && (
                <button 
                  className="risk-manager-btn"
                  onClick={() => setShowRiskManager(showRiskManager === algorithm.id ? null : algorithm.id)}
                >
                  ⚙️ Risk Manager
                </button>
              )}
            </div>

            <p className="algorithm-description">{algorithm.description}</p>

            {/* Risk Management Panel */}
            {showRiskManager === algorithm.id && (
              <div className="risk-management-panel">
                <h4>🛡️ Risk Management Settings</h4>
                <div className="risk-settings-grid">
                  <div className="risk-setting">
                    <label>Max Loss Per Trade (%)</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.maxLossPerTrade}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        maxLossPerTrade: parseFloat(e.target.value)
                      })}
                      step="0.1"
                      min="0.1"
                      max="10"
                    />
                  </div>
                  <div className="risk-setting">
                    <label>Max Daily Loss (%)</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.maxDailyLoss}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        maxDailyLoss: parseFloat(e.target.value)
                      })}
                      step="0.1"
                      min="0.1"
                      max="20"
                    />
                  </div>
                  <div className="risk-setting">
                    <label>Position Size (%)</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.positionSize}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        positionSize: parseFloat(e.target.value)
                      })}
                      step="0.1"
                      min="0.1"
                      max="5"
                    />
                  </div>
                  <div className="risk-setting">
                    <label>Stop Loss (%)</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.stopLoss}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        stopLoss: parseFloat(e.target.value)
                      })}
                      step="0.1"
                      min="0.1"
                      max="10"
                    />
                  </div>
                  <div className="risk-setting">
                    <label>Take Profit (%)</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.takeProfit}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        takeProfit: parseFloat(e.target.value)
                      })}
                      step="0.1"
                      min="0.1"
                      max="20"
                    />
                  </div>
                  <div className="risk-setting">
                    <label>Max Consecutive Losses</label>
                    <input
                      type="number"
                      value={algorithm.riskManagement.maxConsecutiveLosses}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        maxConsecutiveLosses: parseInt(e.target.value)
                      })}
                      min="1"
                      max="10"
                    />
                  </div>
                </div>
                <div className="risk-toggle">
                  <label>
                    <input
                      type="checkbox"
                      checked={algorithm.riskManagement.isEnabled}
                      onChange={(e) => updateRiskManagement(algorithm.id, {
                        isEnabled: e.target.checked
                      })}
                    />
                    Enable Risk Management
                  </label>
                </div>
              </div>
            )}

            <div className="algorithm-stats">
              <div className="stat-group">
                <h4>Performance</h4>
                <div className="stats-grid">
                  <div className="stat">
                    <span className="stat-label">Total Trades</span>
                    <span className="stat-value">{algorithm.performance.totalTrades}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Win Rate</span>
                    <span className="stat-value">{algorithm.performance.winRate}%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Profit Factor</span>
                    <span className="stat-value">{algorithm.performance.profitFactor}</span>
                  </div>
                </div>
              </div>

              <div className="stat-group">
                <h4>ROI Performance</h4>
                <div className="roi-grid">
                  <div className="roi-item">
                    <span className="roi-label">Daily</span>
                    <span className={`roi-value ${algorithm.roi.daily >= 0 ? 'positive' : 'negative'}`}>
                      {algorithm.roi.daily >= 0 ? '+' : ''}{algorithm.roi.daily}%
                    </span>
                  </div>
                  <div className="roi-item">
                    <span className="roi-label">Weekly</span>
                    <span className={`roi-value ${algorithm.roi.weekly >= 0 ? 'positive' : 'negative'}`}>
                      {algorithm.roi.weekly >= 0 ? '+' : ''}{algorithm.roi.weekly}%
                    </span>
                  </div>
                  <div className="roi-item">
                    <span className="roi-label">Monthly</span>
                    <span className={`roi-value ${algorithm.roi.monthly >= 0 ? 'positive' : 'negative'}`}>
                      {algorithm.roi.monthly >= 0 ? '+' : ''}{algorithm.roi.monthly}%
                    </span>
                  </div>
                  <div className="roi-item">
                    <span className="roi-label">Total</span>
                    <span className={`roi-value ${algorithm.roi.total >= 0 ? 'positive' : 'negative'}`}>
                      {algorithm.roi.total >= 0 ? '+' : ''}{algorithm.roi.total}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="algorithm-controls">
              {algorithm.isActive ? (
                <>
                  {!algorithm.isDeployed ? (
                    <div className="deploy-section">
                      <select 
                        value={algorithm.selectedSymbol}
                        onChange={(e) => {
                          const symbol = e.target.value;
                          setAlgorithms(prev => prev.map(algo => 
                            algo.id === algorithm.id 
                              ? { ...algo, selectedSymbol: symbol }
                              : algo
                          ));
                        }}
                        className="symbol-select"
                      >
                        <option value="">Select Symbol</option>
                        {algorithm.availableSymbols.map(symbol => (
                          <option key={symbol} value={symbol}>{symbol}</option>
                        ))}
                      </select>
                      <button 
                        className="deploy-btn"
                        onClick={() => handleDeploy(algorithm.id, algorithm.selectedSymbol)}
                        disabled={!algorithm.selectedSymbol || !selectedAccount}
                      >
                        🚀 Deploy
                      </button>
                    </div>
                  ) : (
                    <div className="active-controls">
                      <div className="symbol-display">
                        Trading: <strong>{algorithm.selectedSymbol}</strong>
                      </div>
                      <div className="control-buttons">
                        <button 
                          className={`control-btn ${algorithm.isPaused ? 'resume' : 'pause'}`}
                          onClick={() => handlePause(algorithm.id)}
                        >
                          {algorithm.isPaused ? '▶️ Resume' : '⏸️ Pause'}
                        </button>
                        <button 
                          className="control-btn stop"
                          onClick={() => handleStop(algorithm.id)}
                        >
                          ⏹️ Stop
                        </button>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="locked-message">
                  <span>🔒 Upgrade subscription to unlock</span>
                  <span className="min-balance">Min. Balance: ${algorithm.minBalance}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Floating Support Widget */}
      <FloatingSupportWidget />
    </div>
  );
};

export default Algorithms;
