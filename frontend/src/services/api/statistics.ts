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
  ea_activity: Array<{
    ea_name: string;
    active_duration: string;
    start_time: string;
  }>;
  profitability_percent: number;
  total_trades: number;
  win_rate: number;
  running_eas: number;
  manual_stats: ManualStats;
}

export const statisticsService = {
  getAccountStatistics: async (): Promise<AccountStatistics> => {
    const response = await api.get('/mt5/account-statistics/');
    return response.data;
  },
};
