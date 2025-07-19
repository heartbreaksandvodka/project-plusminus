import React, { useState, useEffect } from 'react';
import './Algorithms.css';

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

interface SupportTicket {
  id: string;
  subject: string;
  description: string;
  category: 'technical' | 'trading' | 'account' | 'billing';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  createdAt: Date;
  updatedAt: Date;
}

interface ChatMessage {
  id: string;
  message: string;
  sender: 'user' | 'support';
  timestamp: Date;
  isRead: boolean;
}

const Algorithms: React.FC = () => {
  const [algorithms, setAlgorithms] = useState<TradingAlgorithm[]>([]);
  const [userSubscription, setUserSubscription] = useState<any>(null);
  const [mt5Accounts, setMT5Accounts] = useState<any[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  
  // Risk Management States
  const [showRiskManager, setShowRiskManager] = useState<string | null>(null);
  
  // Customer Support States
  const [showSupportChat, setShowSupportChat] = useState(false);
  const [showTicketForm, setShowTicketForm] = useState(false);
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [supportTickets, setSupportTickets] = useState<SupportTicket[]>([]);

  useEffect(() => {
    // Load algorithms based on user subscription
    loadUserSubscription();
    loadMT5Accounts();
    
    // Mock trading algorithms data
    const mockAlgorithms: TradingAlgorithm[] = [
    {
      id: '1',
      name: 'Scalping Master Pro',
      description: 'High-frequency scalping algorithm that targets small price movements in major forex pairs. Uses advanced order flow analysis and executes 50-100 trades per day.',
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
      name: 'Trend Rider Elite',
      description: 'Long-term trend following strategy that identifies and rides major market trends. Perfect for capturing significant moves in forex and indices.',
      category: 'forex',
      riskLevel: 'Low',
      minBalance: 2000,
      isActive: true,
      isDeployed: true,
      isPaused: false,
      roi: { daily: 0.3, weekly: 2.1, monthly: 9.8, total: 87.3 },
      performance: { totalTrades: 342, winRate: 78.2, profitFactor: 2.34 },
      selectedSymbol: 'EURUSD',
      availableSymbols: ['EURUSD', 'GBPUSD', 'US30', 'SPX500'],
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
    },
    {
      id: '3',
      name: 'Breakout Hunter',
      description: 'Identifies key support and resistance breakouts with high probability setups. Specializes in stocks and crypto markets during high volatility periods.',
      category: 'stocks',
      riskLevel: 'High',
      minBalance: 5000,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 1.2, weekly: 7.8, monthly: 32.1, total: 298.4 },
      performance: { totalTrades: 892, winRate: 62.1, profitFactor: 2.12 },
      selectedSymbol: '',
      availableSymbols: ['AAPL', 'TSLA', 'GOOGL', 'MSFT'],
      riskManagement: {
        maxLossPerTrade: 3.0,
        maxDailyLoss: 8.0,
        maxDrawdown: 20.0,
        positionSize: 1.5,
        stopLoss: 2.5,
        takeProfit: 5.0,
        maxConsecutiveLosses: 4,
        isEnabled: true
      }
    },
    {
      id: '4',
      name: 'Crypto Momentum',
      description: 'Advanced momentum strategy designed for cryptocurrency markets. Uses machine learning to predict short-term price movements in major crypto pairs.',
      category: 'crypto',
      riskLevel: 'High',
      minBalance: 3000,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 2.1, weekly: 12.3, monthly: 45.6, total: 423.8 },
      performance: { totalTrades: 1563, winRate: 59.8, profitFactor: 1.92 },
      selectedSymbol: '',
      availableSymbols: ['BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD'],
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
      id: '5',
      name: 'Grid Trading Pro',
      description: 'Systematic grid trading algorithm that profits from market volatility. Places buy and sell orders at regular intervals above and below current price.',
      category: 'forex',
      riskLevel: 'Medium',
      minBalance: 1500,
      isActive: false,
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
      id: '6',
      name: 'News Impact Trader',
      description: 'Reacts to major economic news releases and market events. Uses natural language processing to analyze news sentiment and execute trades accordingly.',
      category: 'forex',
      riskLevel: 'High',
      minBalance: 4000,
      isActive: false,
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
      id: '7',
      name: 'Arbitrage Master',
      description: 'Exploits price differences between different exchanges and markets. Low-risk strategy with consistent returns through statistical arbitrage opportunities.',
      category: 'crypto',
      riskLevel: 'Low',
      minBalance: 10000,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 0.2, weekly: 1.4, monthly: 6.8, total: 42.3 },
      performance: { totalTrades: 3421, winRate: 89.7, profitFactor: 3.12 },
      selectedSymbol: '',
      availableSymbols: ['BTCUSD', 'ETHUSD'],
      riskManagement: {
        maxLossPerTrade: 1.0,
        maxDailyLoss: 2.0,
        maxDrawdown: 5.0,
        positionSize: 3.0,
        stopLoss: 1.0,
        takeProfit: 2.0,
        maxConsecutiveLosses: 2,
        isEnabled: true
      }
    },
    {
      id: '8',
      name: 'Mean Reversion AI',
      description: 'AI-powered mean reversion strategy that identifies overbought and oversold conditions. Uses machine learning models trained on historical price patterns.',
      category: 'stocks',
      riskLevel: 'Medium',
      minBalance: 3500,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 0.7, weekly: 4.8, monthly: 21.3, total: 178.9 },
      performance: { totalTrades: 1124, winRate: 71.2, profitFactor: 1.98 },
      selectedSymbol: '',
      availableSymbols: ['SPY', 'QQQ', 'DIA', 'IWM'],
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
      name: 'Swing Master Pro',
      description: 'Multi-timeframe swing trading algorithm that holds positions for 2-10 days. Combines technical analysis with market structure for high-probability setups.',
      category: 'indices',
      riskLevel: 'Medium',
      minBalance: 2500,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 0.4, weekly: 2.8, monthly: 12.6, total: 98.7 },
      performance: { totalTrades: 287, winRate: 76.8, profitFactor: 2.67 },
      selectedSymbol: '',
      availableSymbols: ['US30', 'SPX500', 'NAS100', 'GER40'],
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
      id: '10',
      name: 'Options Wheel Strategy',
      description: 'Systematic options trading strategy that sells puts and covered calls. Generates consistent income through premium collection in sideways markets.',
      category: 'stocks',
      riskLevel: 'Low',
      minBalance: 8000,
      isActive: false,
      isDeployed: false,
      isPaused: false,
      roi: { daily: 0.3, weekly: 2.1, monthly: 9.2, total: 67.4 },
      performance: { totalTrades: 156, winRate: 84.6, profitFactor: 2.89 },
      selectedSymbol: '',
      availableSymbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
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
    }
    ];

    setAlgorithms(mockAlgorithms);
  }, []);

  const loadUserSubscription = async () => {
    // TODO: Fetch from API
    setUserSubscription({
      plan_type: 'premium',
      max_algorithms: 5,
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

  // Customer Support Functions
  const sendMessage = (message: string) => {
    const newMsg: ChatMessage = {
      id: Date.now().toString(),
      message,
      sender: 'user',
      timestamp: new Date(),
      isRead: false
    };
    setChatMessages(prev => [...prev, newMsg]);
    setNewMessage('');
    
    // Simulate support response
    setTimeout(() => {
      const supportMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: 'Thank you for your message. Our support team will assist you shortly.',
        sender: 'support',
        timestamp: new Date(),
        isRead: false
      };
      setChatMessages(prev => [...prev, supportMsg]);
    }, 2000);
  };

  const createSupportTicket = (ticket: Omit<SupportTicket, 'id' | 'createdAt' | 'updatedAt' | 'status'>) => {
    const newTicket: SupportTicket = {
      ...ticket,
      id: Date.now().toString(),
      status: 'open',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setSupportTickets(prev => [...prev, newTicket]);
    setShowTicketForm(false);
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

        {/* Customer Support Panel */}
        <div className="support-panel">
          <button 
            className="support-btn chat-btn"
            onClick={() => setShowSupportChat(true)}
          >
            💬 Live Chat
          </button>
          <button 
            className="support-btn ticket-btn"
            onClick={() => setShowTicketForm(true)}
          >
            🎫 Create Ticket
          </button>
          <button 
            className="support-btn kb-btn"
            onClick={() => setShowKnowledgeBase(true)}
          >
            📚 Knowledge Base
          </button>
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

      {/* Live Chat Modal */}
      {showSupportChat && (
        <div className="modal-overlay" onClick={() => setShowSupportChat(false)}>
          <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
            <div className="chat-header">
              <h3>💬 Live Support Chat</h3>
              <button onClick={() => setShowSupportChat(false)}>✕</button>
            </div>
            <div className="chat-messages">
              {chatMessages.map(msg => (
                <div key={msg.id} className={`chat-message ${msg.sender}`}>
                  <div className="message-content">{msg.message}</div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                onKeyPress={(e) => e.key === 'Enter' && sendMessage(newMessage)}
              />
              <button onClick={() => sendMessage(newMessage)}>Send</button>
            </div>
          </div>
        </div>
      )}

      {/* Support Ticket Modal */}
      {showTicketForm && (
        <div className="modal-overlay" onClick={() => setShowTicketForm(false)}>
          <div className="ticket-modal" onClick={(e) => e.stopPropagation()}>
            <div className="ticket-header">
              <h3>🎫 Create Support Ticket</h3>
              <button onClick={() => setShowTicketForm(false)}>✕</button>
            </div>
            <form className="ticket-form" onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target as HTMLFormElement);
              createSupportTicket({
                subject: formData.get('subject') as string,
                description: formData.get('description') as string,
                category: formData.get('category') as any,
                priority: formData.get('priority') as any
              });
            }}>
              <div className="form-group">
                <label>Subject</label>
                <input type="text" name="subject" required />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select name="category" required>
                  <option value="">Select Category</option>
                  <option value="technical">Technical Issue</option>
                  <option value="trading">Trading Support</option>
                  <option value="account">Account Management</option>
                  <option value="billing">Billing</option>
                </select>
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select name="priority" required>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea name="description" rows={4} required></textarea>
              </div>
              <button type="submit" className="submit-ticket-btn">Create Ticket</button>
            </form>
          </div>
        </div>
      )}

      {/* Knowledge Base Modal */}
      {showKnowledgeBase && (
        <div className="modal-overlay" onClick={() => setShowKnowledgeBase(false)}>
          <div className="kb-modal" onClick={(e) => e.stopPropagation()}>
            <div className="kb-header">
              <h3>📚 Knowledge Base</h3>
              <button onClick={() => setShowKnowledgeBase(false)}>✕</button>
            </div>
            <div className="kb-content">
              <div className="kb-section">
                <h4>🚀 Getting Started</h4>
                <ul>
                  <li>How to connect your MT5 account</li>
                  <li>Understanding algorithm risk levels</li>
                  <li>Setting up your first trading algorithm</li>
                  <li>Account balance requirements</li>
                </ul>
              </div>
              <div className="kb-section">
                <h4>⚙️ Risk Management</h4>
                <ul>
                  <li>Configuring stop loss and take profit</li>
                  <li>Position sizing strategies</li>
                  <li>Maximum drawdown settings</li>
                  <li>Daily loss limits</li>
                </ul>
              </div>
              <div className="kb-section">
                <h4>📊 Performance Analysis</h4>
                <ul>
                  <li>Reading ROI metrics</li>
                  <li>Understanding win rates</li>
                  <li>Profit factor calculations</li>
                  <li>Performance optimization tips</li>
                </ul>
              </div>
              <div className="kb-section">
                <h4>🔧 Troubleshooting</h4>
                <ul>
                  <li>Algorithm not deploying</li>
                  <li>MT5 connection issues</li>
                  <li>Performance problems</li>
                  <li>Account access issues</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Algorithms;
