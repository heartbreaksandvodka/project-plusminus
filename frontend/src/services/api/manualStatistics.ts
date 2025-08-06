import api from './client';

export interface ManualSession {
  session_start: string;
  session_end: string | null;
  trades_executed: number;
  profit_loss: number;
}

export interface ManualStatistics {
  total_trades: number;
  profitability_percent: number;
  win_rate: number;
  sessions: ManualSession[];
}

export const manualStatisticsService = {
  getManualStatistics: async (): Promise<ManualStatistics> => {
    const response = await api.get('/mt5/manual-statistics/');
    return response.data;
  },
};
