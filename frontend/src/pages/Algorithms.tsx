import React, { useState, useEffect } from 'react';
import './Algorithms.css';
import { FloatingSupportWidget } from '../components/Support';

interface RiskManagement {
  maxLossPerTrade: number; // percentage
  maxDailyLoss: number; // percentage
  maxDrawdown: number; // percentage
  positionSize: number; // percentage of account
  stopLoss: number; // percentage
  takeProfit: number; // percentage
  maxConsecutiveLosses: number;
  isEnabled: boolean;
}

interface TradingAlgorithm {
  id: string;
  name: string;
  description: string;
  category: 'forex' | 'stocks' | 'crypto' | 'indices';
  riskLevel: 'Low' | 'Medium' | 'High';
  minBalance: number;
  isActive: boolean;
  isDeployed: boolean;
  isPaused: boolean;
  roi: {
    daily: number;
    weekly: number;
    monthly: number;
    total: number;
  };
  performance: {
    totalTrades: number;
    winRate: number;
    profitFactor: number;
  };
  selectedSymbol: string;
  availableSymbols: string[];
  riskManagement: RiskManagement;
}

const Algorithms: React.FC = () => {
  const [algorithms, setAlgorithms] = useState<TradingAlgorithm[]>([]);
  const [userSubscription, setUserSubscription] = useState<any>(null);
  const [mt5Accounts, setMT5Accounts] = useState<any[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  
  // Risk Management States
  const [showRiskManager, setShowRiskManager] = useState<string | null>(null);

  useEffect(() => {
    // Load algorithms based on user subscription
    loadUserSubscription();
    loadMT5Accounts();
    
    // Mock trading algorithms data
    const mockAlgorithms: TradingAlgorithm[] = [
      {
        id: '1',
        name: 'Candy EA',
        description: 'M1 execution with higher timeframe trend and RSI cross.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.8, weekly: 4.2, monthly: 18.5, total: 156.7 },
        performance: { totalTrades: 1247, winRate: 68.5, profitFactor: 1.85 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
        riskManagement: {
          maxLossPerTrade: 2.0,
          maxDailyLoss: 5.0,
          maxDrawdown: 15.0,
          positionSize: 1.0,
          stopLoss: 1.5,
          takeProfit: 3.0,
          maxConsecutiveLosses: 3,
          isEnabled: true
        }
      },
      {
        id: '2',
        name: 'Grid Trading EA',
        description: 'Systematic grid trading for volatility, buy/sell at intervals.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.5, weekly: 3.2, monthly: 14.7, total: 132.5 },
        performance: { totalTrades: 2341, winRate: 72.3, profitFactor: 1.67 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'ETHUSD'],
        riskManagement: {
          maxLossPerTrade: 2.0,
          maxDailyLoss: 4.0,
          maxDrawdown: 12.0,
          positionSize: 1.2,
          stopLoss: 1.8,
          takeProfit: 3.5,
          maxConsecutiveLosses: 3,
          isEnabled: true
        }
      },
      {
        id: '3',
        name: 'High-Frequency Scalping EA',
        description: 'Tick-based scalping, order flow analysis, 50-100 trades/day.',
        category: 'forex',
        riskLevel: 'High',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 1.2, weekly: 7.8, monthly: 32.1, total: 298.4 },
        performance: { totalTrades: 1563, winRate: 65.4, profitFactor: 1.92 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY'],
        riskManagement: {
          maxLossPerTrade: 4.0,
          maxDailyLoss: 10.0,
          maxDrawdown: 25.0,
          positionSize: 1.5,
          stopLoss: 3.0,
          takeProfit: 6.0,
          maxConsecutiveLosses: 5,
          isEnabled: true
        }
      },
      {
        id: '4',
        name: 'Indices Hedging EA',
        description: 'Dynamic partial hedging for indices, volatility-based.',
        category: 'indices',
        riskLevel: 'Medium',
        minBalance: 2500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.4, weekly: 2.8, monthly: 12.6, total: 98.7 },
        performance: { totalTrades: 287, winRate: 76.8, profitFactor: 2.67 },
        selectedSymbol: '',
        availableSymbols: ['US500', 'DE30'],
        riskManagement: {
          maxLossPerTrade: 2.5,
          maxDailyLoss: 5.0,
          maxDrawdown: 12.0,
          positionSize: 2.0,
          stopLoss: 2.0,
          takeProfit: 4.5,
          maxConsecutiveLosses: 3,
          isEnabled: true
        }
      },
      {
        id: '5',
        name: 'Indices Martingale EA',
        description: 'Adaptive grid martingale for indices, dynamic lot sizing.',
        category: 'indices',
        riskLevel: 'High',
        minBalance: 3000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 2.1, weekly: 12.3, monthly: 45.6, total: 423.8 },
        performance: { totalTrades: 892, winRate: 62.1, profitFactor: 2.12 },
        selectedSymbol: '',
        availableSymbols: ['US500', 'DE30'],
        riskManagement: {
          maxLossPerTrade: 4.0,
          maxDailyLoss: 10.0,
          maxDrawdown: 25.0,
          positionSize: 1.5,
          stopLoss: 3.0,
          takeProfit: 6.0,
          maxConsecutiveLosses: 5,
          isEnabled: true
        }
      },
      {
        id: '6',
        name: 'Liquidity Detector EA',
        description: 'Detects liquidity pools and FVG, institutional entries.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.5, weekly: 3.2, monthly: 14.7, total: 132.5 },
        performance: { totalTrades: 2341, winRate: 72.3, profitFactor: 1.67 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY'],
        riskManagement: {
          maxLossPerTrade: 2.0,
          maxDailyLoss: 4.0,
          maxDrawdown: 12.0,
          positionSize: 1.2,
          stopLoss: 1.8,
          takeProfit: 3.5,
          maxConsecutiveLosses: 3,
          isEnabled: true
        }
      },
      {
        id: '7',
        name: 'News EA',
        description: 'Trades news events with dynamic risk management.',
        category: 'forex',
        riskLevel: 'High',
        minBalance: 4000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 1.8, weekly: 9.4, monthly: 38.2, total: 287.6 },
        performance: { totalTrades: 456, winRate: 65.4, profitFactor: 2.45 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'GOLD'],
        riskManagement: {
          maxLossPerTrade: 3.5,
          maxDailyLoss: 8.0,
          maxDrawdown: 18.0,
          positionSize: 1.8,
          stopLoss: 2.8,
          takeProfit: 5.5,
          maxConsecutiveLosses: 4,
          isEnabled: true
        }
      },
      {
        id: '8',
        name: 'Smart Hedging EA',
        description: 'Dynamic hedging for any market, volatility-based.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 2000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.7, weekly: 4.8, monthly: 21.3, total: 178.9 },
        performance: { totalTrades: 1124, winRate: 71.2, profitFactor: 1.98 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'US500', 'DE30'],
        riskManagement: {
          maxLossPerTrade: 2.5,
          maxDailyLoss: 6.0,
          maxDrawdown: 15.0,
          positionSize: 1.8,
          stopLoss: 2.0,
          takeProfit: 4.0,
          maxConsecutiveLosses: 3,
          isEnabled: true
        }
      },
      {
        id: '9',
        name: 'Trailing Stop EA',
        description: 'Manages trailing stops for open positions.',
        category: 'forex',
        riskLevel: 'Low',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.3, weekly: 2.1, monthly: 9.2, total: 67.4 },
        performance: { totalTrades: 156, winRate: 84.6, profitFactor: 2.89 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD'],
        riskManagement: {
          maxLossPerTrade: 1.5,
          maxDailyLoss: 3.0,
          maxDrawdown: 8.0,
          positionSize: 2.5,
          stopLoss: 1.5,
          takeProfit: 3.0,
          maxConsecutiveLosses: 2,
          isEnabled: true
        }
      },
      {
        id: '10',
        name: 'Trend Following EA',
        description: 'Long-term trend following with multi-timeframe analysis.',
        category: 'forex',
        riskLevel: 'Low',
        minBalance: 2000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        roi: { daily: 0.3, weekly: 2.1, monthly: 9.8, total: 87.3 },
        performance: { totalTrades: 342, winRate: 78.2, profitFactor: 2.34 },
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'US500', 'DE30'],
        riskManagement: {
          maxLossPerTrade: 1.5,
          maxDailyLoss: 3.0,
          maxDrawdown: 10.0,
          positionSize: 2.0,
          stopLoss: 2.0,
          takeProfit: 4.0,
          maxConsecutiveLosses: 2,
          isEnabled: true
        }
      }
    ];

    setAlgorithms(mockAlgorithms);
  }, []);

  const loadUserSubscription = async () => {
    // TODO: Fetch from API
    setUserSubscription({
      plan_type: 'pro',
      max_algorithms: 10,
      max_mt5_accounts: 2
    });
  };

  const loadMT5Accounts = async () => {
    // TODO: Fetch from MT5 API
    setMT5Accounts([
      { id: '1', account_number: '12345678', broker: 'Exness', status: 'connected' },
      { id: '2', account_number: '87654321', broker: 'IC Markets', status: 'connected' }
    ]);
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
  const updateRiskManagement = (algorithmId: string, riskSettings: Partial<RiskManagement>) => {
    setAlgorithms(prev => prev.map(algo => 
      algo.id === algorithmId 
        ? { ...algo, riskManagement: { ...algo.riskManagement, ...riskSettings } }
        : algo
    ));
  };

  const validateRiskSettings = (settings: RiskManagement): string[] => {
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
