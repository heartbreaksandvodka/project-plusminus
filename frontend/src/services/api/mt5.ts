import api from './client';
import { MT5Account, MT5AccountForm, MT5ConnectionTest, AlgorithmExecution } from '../../types/mt5';

export const mt5Service = {
  // Get user's MT5 account
  getAccount: async (): Promise<MT5Account> => {
    const response = await api.get('/mt5/account/');
    return response.data;
  },

  // Create or update MT5 account
  saveAccount: async (accountData: MT5AccountForm): Promise<{ account: MT5Account; connection: any }> => {
    const response = await api.post('/mt5/account/', accountData);
    return response.data;
  },

  // Test MT5 connection
  testConnection: async (connectionData: MT5ConnectionTest): Promise<any> => {
    const response = await api.post('/mt5/test-connection/', connectionData);
    return response.data;
  },

  // Refresh account status
  refreshStatus: async (): Promise<{ account: MT5Account; connection: any }> => {
    const response = await api.post('/mt5/refresh-status/');
    return response.data;
  },

  // Delete MT5 account
  deleteAccount: async (): Promise<any> => {
    const response = await api.delete('/mt5/delete-account/');
    return response.data;
  },

  // Get algorithm executions
  getAlgorithmExecutions: async (): Promise<AlgorithmExecution[]> => {
    const response = await api.get('/mt5/algorithms/');
    return response.data;
  },

  // Start algorithm
  startAlgorithm: async (algorithmName: string): Promise<any> => {
    const response = await api.post('/mt5/start-algorithm/', {
      algorithm_name: algorithmName
    });
    return response.data;
  },

  // Stop algorithm
  stopAlgorithm: async (executionId: number): Promise<any> => {
    const response = await api.post(`/mt5/stop-algorithm/${executionId}/`);
    return response.data;
  },
};
