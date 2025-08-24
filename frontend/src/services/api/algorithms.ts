import api from './client';

export interface Algorithm {
  id: string;
  name: string;
  description: string;
  category: 'forex' | 'stocks' | 'crypto' | 'indices';
  riskLevel: 'Low' | 'Medium' | 'High';
  minBalance: number;
  isActive: boolean;
  isDeployed: boolean;
  isPaused: boolean;
  executionId?: number;
  selectedSymbol: string;
  availableSymbols: string[];
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
  riskManagement: {
    maxLossPerTrade: number;
    maxDailyLoss: number;
    maxDrawdown: number;
    positionSize: number;
    stopLoss: number;
    takeProfit: number;
    maxConsecutiveLosses: number;
    isEnabled: boolean;
  };
}

export interface AlgorithmExecution {
  id: number;
  algorithm_name: string;
  execution_status: 'running' | 'stopped' | 'paused' | 'error' | 'completed';
  started_at: string;
  stopped_at?: string;
  profit_loss: number;
  trades_count: number;
  pid?: number;
  error_message?: string;
  last_heartbeat?: string;
  symbol?: string;
}

export interface AlgorithmStatus {
  execution: AlgorithmExecution;
  real_time_status: {
    is_running: boolean;
    current_pnl: number;
    positions_count: number;
    last_trade_time?: string;
    error_message?: string;
  };
  performance_metrics: {
    daily_roi: number;
    weekly_roi: number;
    monthly_roi: number;
    win_rate: number;
    total_trades: number;
    profit_factor: number;
  };
}

export const algorithmsService = {
  // Get available algorithms (static list with dynamic status)
  getAvailableAlgorithms: async (): Promise<Algorithm[]> => {
    // This returns the available algorithms based on subscription
    // The actual execution status comes from getExecutions()
    return [
      {
        id: 'candy_ea',
        name: 'Candy EA',
        description: 'M1 execution with higher timeframe trend and RSI cross.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
        roi: { daily: 0.8, weekly: 4.2, monthly: 18.5, total: 156.7 },
        performance: { totalTrades: 1247, winRate: 68.5, profitFactor: 1.85 },
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
        id: 'grid_trading_ea',
        name: 'Grid Trading EA',
        description: 'Systematic grid trading for volatility, buy/sell at intervals.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'ETHUSD'],
        roi: { daily: 0.5, weekly: 3.2, monthly: 14.7, total: 132.5 },
        performance: { totalTrades: 2341, winRate: 72.3, profitFactor: 1.67 },
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
        id: 'hf_scalping_ea',
        name: 'High-Frequency Scalping EA',
        description: 'Tick-based scalping, order flow analysis, 50-100 trades/day.',
        category: 'forex',
        riskLevel: 'High',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY'],
        roi: { daily: 1.2, weekly: 7.8, monthly: 32.1, total: 298.4 },
        performance: { totalTrades: 1563, winRate: 65.4, profitFactor: 1.92 },
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
        id: 'indices_hedging_ea',
        name: 'Indices Hedging EA',
        description: 'Dynamic partial hedging for indices, volatility-based.',
        category: 'indices',
        riskLevel: 'Medium',
        minBalance: 2500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['US500', 'DE30'],
        roi: { daily: 0.4, weekly: 2.8, monthly: 12.6, total: 98.7 },
        performance: { totalTrades: 287, winRate: 76.8, profitFactor: 2.67 },
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
        id: 'indices_martingale_ea',
        name: 'Indices Martingale EA',
        description: 'Adaptive grid martingale for indices, dynamic lot sizing.',
        category: 'indices',
        riskLevel: 'High',
        minBalance: 3000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['US500', 'DE30'],
        roi: { daily: 2.1, weekly: 12.3, monthly: 45.6, total: 423.8 },
        performance: { totalTrades: 892, winRate: 62.1, profitFactor: 2.12 },
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
        id: 'liquidity_ea',
        name: 'Liquidity Detector EA',
        description: 'Detects liquidity pools and FVG, institutional entries.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 1500,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY'],
        roi: { daily: 0.5, weekly: 3.2, monthly: 14.7, total: 132.5 },
        performance: { totalTrades: 2341, winRate: 72.3, profitFactor: 1.67 },
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
        id: 'news_ea',
        name: 'News EA',
        description: 'Trades news events with dynamic risk management.',
        category: 'forex',
        riskLevel: 'High',
        minBalance: 4000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'GOLD'],
        roi: { daily: 1.8, weekly: 9.4, monthly: 38.2, total: 287.6 },
        performance: { totalTrades: 456, winRate: 65.4, profitFactor: 2.45 },
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
        id: 'smart_hedging_ea',
        name: 'Smart Hedging EA',
        description: 'Dynamic hedging for any market, volatility-based.',
        category: 'forex',
        riskLevel: 'Medium',
        minBalance: 2000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'US500', 'DE30'],
        roi: { daily: 0.7, weekly: 4.8, monthly: 21.3, total: 178.9 },
        performance: { totalTrades: 1124, winRate: 71.2, profitFactor: 1.98 },
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
        id: 'trailing_stop_ea',
        name: 'Trailing Stop EA',
        description: 'Manages trailing stops for open positions.',
        category: 'forex',
        riskLevel: 'Low',
        minBalance: 1000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD'],
        roi: { daily: 0.3, weekly: 2.1, monthly: 9.2, total: 67.4 },
        performance: { totalTrades: 156, winRate: 84.6, profitFactor: 2.89 },
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
        id: 'trend_following_ea',
        name: 'Trend Following EA',
        description: 'Long-term trend following with multi-timeframe analysis.',
        category: 'forex',
        riskLevel: 'Low',
        minBalance: 2000,
        isActive: true,
        isDeployed: false,
        isPaused: false,
        selectedSymbol: '',
        availableSymbols: ['EURUSD', 'GBPUSD', 'US500', 'DE30'],
        roi: { daily: 0.3, weekly: 2.1, monthly: 9.8, total: 87.3 },
        performance: { totalTrades: 342, winRate: 78.2, profitFactor: 2.34 },
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
  },

  // Get algorithm executions (real backend API call)
  getExecutions: async (): Promise<AlgorithmExecution[]> => {
    try {
      const response = await api.get('/mt5/algorithms/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch algorithm executions:', error);
      return [];
    }
  },

  // Start algorithm (real backend API call)
  startAlgorithm: async (algorithmName: string, symbol: string): Promise<any> => {
    try {
      const response = await api.post('/mt5/start-algorithm/', {
        algorithm_name: algorithmName,
        symbol: symbol
      });
      return response.data;
    } catch (error) {
      console.error('Failed to start algorithm:', error);
      throw error;
    }
  },

  // Pause algorithm (real backend API call)
  pauseAlgorithm: async (executionId: number, algorithmName: string): Promise<any> => {
    try {
      const response = await api.post(`/mt5/pause-algorithm/${executionId}/`, {
        algorithm_name: algorithmName
      });
      return response.data;
    } catch (error) {
      console.error('Failed to pause algorithm:', error);
      throw error;
    }
  },

  // Resume algorithm (real backend API call)
  resumeAlgorithm: async (executionId: number, algorithmName: string): Promise<any> => {
    try {
      const response = await api.post(`/mt5/resume-algorithm/${executionId}/`, {
        algorithm_name: algorithmName
      });
      return response.data;
    } catch (error) {
      console.error('Failed to resume algorithm:', error);
      throw error;
    }
  },

  // Stop algorithm (real backend API call)
  stopAlgorithm: async (executionId: number): Promise<any> => {
    try {
      const response = await api.post(`/mt5/stop-algorithm/${executionId}/`);
      return response.data;
    } catch (error) {
      console.error('Failed to stop algorithm:', error);
      throw error;
    }
  },

  // Get algorithm status (polling endpoint)
  getAlgorithmStatus: async (executionId: number): Promise<AlgorithmStatus> => {
    try {
      const response = await api.get(`/mt5/algorithm-status/${executionId}/`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch algorithm status:', error);
      throw error;
    }
  },

  // Merge static algorithms with dynamic execution data
  mergeAlgorithmsWithExecutions: (algorithms: Algorithm[], executions: AlgorithmExecution[]): Algorithm[] => {
    return algorithms.map(algo => {
      const execution = executions.find(exec => exec.algorithm_name === algo.id);
      if (execution) {
        return {
          ...algo,
          isDeployed: execution.execution_status === 'running' || execution.execution_status === 'paused',
          isPaused: execution.execution_status === 'paused',
          executionId: execution.id,
          selectedSymbol: execution.symbol || ''
        };
      }
      return algo;
    });
  }
};

export default algorithmsService;
