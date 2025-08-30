import api from './client';

export interface ManualSession {
  session_start: string;
  session_end: string | null;
  trades_executed: number;
  profit_loss: number;
}

export interface ManualStats {
  total_trades: number;
  profitability_percent: number;
  win_rate: number;
  sessions: ManualSession[];
}

export interface AccountStatistics {
  // EA Statistics
  ea_activity: Array<{
    ea_name: string;
    active_duration: string;
    start_time: string;
  }>;
  ea_profitability_percent: number;
  ea_total_trades: number;
  ea_win_rate: number;
  running_eas: number;
  
  // Manual Trading Statistics
  manual_stats: ManualStats;
  
  // Legacy fields for backward compatibility
  profitability_percent: number;
  total_trades: number;
  win_rate: number;
}

export const statisticsService = {
  getAccountStatistics: async (): Promise<AccountStatistics> => {
    const response = await api.get('/mt5/account-statistics/');
    return response.data;
  },
};
