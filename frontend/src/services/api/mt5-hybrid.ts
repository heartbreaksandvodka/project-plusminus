import api, { eaServiceApi } from './client';
import { MT5Account, MT5ConnectionTest, AlgorithmExecution } from '../../types/mt5';

export const mt5Service = {
  // MT5 Account Management (Django Backend)
  getAccount: async (): Promise<MT5Account> => {
    const response = await api.get('/mt5/account/');
    return response.data;
  },

  createAccount: async (accountData: Partial<MT5Account>): Promise<MT5Account> => {
    const response = await api.post('/mt5/account/', accountData);
    return response.data;
  },

  updateAccount: async (accountData: Partial<MT5Account>): Promise<MT5Account> => {
    const response = await api.put('/mt5/account/', accountData);
    return response.data;
  },

  // Unified save method for create/update (used by MT5AccountCard)
  saveAccount: async (accountData: any): Promise<{ account: MT5Account; connection: any }> => {
    const response = await api.post('/mt5/account/', accountData);
    return response.data;
  },

  testConnection: async (connectionData: MT5ConnectionTest): Promise<any> => {
    const response = await api.post('/mt5/test-connection/', connectionData);
    return response.data;
  },

  refreshStatus: async (): Promise<{ account: MT5Account; connection: any }> => {
    const response = await api.post('/mt5/refresh-status/');
    return response.data;
  },

  deleteAccount: async (): Promise<any> => {
    const response = await api.delete('/mt5/delete-account/');
    return response.data;
  },

  // Algorithm Management (Hybrid: Django + EA Service)
  getAlgorithmExecutions: async (): Promise<AlgorithmExecution[]> => {
    const response = await api.get('/mt5/algorithms/');
    return response.data;
  },

  // EA Service Integration
  getAvailableAlgorithms: async (): Promise<any[]> => {
    try {
      const response = await eaServiceApi.get('/algorithms');
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, falling back to Django backend');
      // Fallback to Django backend
      const response = await api.get('/mt5/available-algorithms/');
      return response.data;
    }
  },

  getAllAlgorithmStatus: async (): Promise<any[]> => {
    try {
      const response = await eaServiceApi.get('/algorithms/status');
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, falling back to Django backend');
      return [];
    }
  },

  startAlgorithm: async (algorithmName: string, symbol?: string): Promise<any> => {
    try {
      // Try EA Service first
      const response = await eaServiceApi.post(`/algorithms/${algorithmName}/start`, {
        symbol: symbol || 'EURUSD'
      });
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, using Django backend');
      // Fallback to Django backend
      const response = await api.post('/mt5/start-algorithm/', {
        algorithm_name: algorithmName,
        symbol: symbol
      });
      return response.data;
    }
  },

  stopAlgorithm: async (executionId: number | string): Promise<any> => {
    try {
      // Try EA Service first
      const response = await eaServiceApi.post(`/algorithms/${executionId}/stop`);
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, using Django backend');
      // Fallback to Django backend
      const response = await api.post('/mt5/stop-algorithm/', {
        execution_id: executionId
      });
      return response.data;
    }
  },

  pauseAlgorithm: async (executionId: number | string): Promise<any> => {
    try {
      // Try EA Service first
      const response = await eaServiceApi.post(`/algorithms/${executionId}/pause`);
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, using Django backend');
      // Fallback to Django backend
      const response = await api.post('/mt5/pause-algorithm/', {
        execution_id: executionId
      });
      return response.data;
    }
  },

  resumeAlgorithm: async (executionId: number | string): Promise<any> => {
    try {
      // Try EA Service first
      const response = await eaServiceApi.post(`/algorithms/${executionId}/resume`);
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, using Django backend');
      // Fallback to Django backend
      const response = await api.post('/mt5/resume-algorithm/', {
        execution_id: executionId
      });
      return response.data;
    }
  },

  getAlgorithmStatus: async (executionId: number | string): Promise<any> => {
    try {
      // Try EA Service first
      const response = await eaServiceApi.get(`/algorithms/${executionId}/status`);
      return response.data;
    } catch (error) {
      console.warn('EA Service not available, using Django backend');
      // Fallback to Django backend
      const response = await api.get(`/mt5/algorithm/${executionId}/status/`);
      return response.data;
    }
  },

  // WebSocket Connection (EA Service with fallback)
  connectToAlgorithmUpdates: (executionId: string, onMessage: (data: any) => void) => {
    // Try EA Service WebSocket first
    try {
      const ws = new WebSocket(`ws://localhost:8001/ws/algorithms/${executionId}`);
      
      ws.onopen = () => {
        console.log('Connected to EA Service WebSocket');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
      };
      
      ws.onerror = (error) => {
        console.warn('EA Service WebSocket error:', error);
        ws.close();
      };
      
      ws.onclose = () => {
        console.warn('EA Service WebSocket closed, consider fallback');
      };
      
      return ws;
    } catch (error) {
      console.warn('WebSocket connection failed:', error);
      return null;
    }
  },

  // Fallback WebSocket connection to Django
  connectToAlgorithmUpdatesFallback: (executionId: string, onMessage: (data: any) => void) => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/algorithm/${executionId}/`);
      
      ws.onopen = () => {
        console.log('Connected to Django WebSocket (fallback)');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
      };
      
      return ws;
    } catch (error) {
      console.warn('Fallback WebSocket connection failed:', error);
      return null;
    }
  },

  // Django Backend Only Endpoints
  getAlgorithmAnalytics: async (executionId: number): Promise<any> => {
    const response = await api.get(`/mt5/algorithm/${executionId}/analytics/`);
    return response.data;
  },

  getAlgorithmTrades: async (executionId: number): Promise<any> => {
    const response = await api.get(`/mt5/algorithm/${executionId}/trades/`);
    return response.data;
  },

  // Service Health Check
  checkEAServiceHealth: async (): Promise<boolean> => {
    try {
      const response = await eaServiceApi.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  },

  getServiceStatus: async (): Promise<any> => {
    try {
      const response = await eaServiceApi.get('/service/status');
      return response.data;
    } catch (error) {
      return { status: 'unavailable', message: 'EA Service not reachable' };
    }
  }
};

export default mt5Service;
