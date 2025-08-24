import { useState, useEffect, useCallback } from 'react';
import algorithmsService, { AlgorithmExecution, AlgorithmStatus } from '../services/api/algorithms';

export interface UseAlgorithmStatusOptions {
  executionId?: number;
  pollingInterval?: number;
  enabled?: boolean;
}

export interface AlgorithmStatusState {
  status: AlgorithmStatus | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export const useAlgorithmStatus = (options: UseAlgorithmStatusOptions = {}) => {
  const {
    executionId,
    pollingInterval = 5000, // 5 seconds default
    enabled = true
  } = options;

  const [state, setState] = useState<AlgorithmStatusState>({
    status: null,
    loading: false,
    error: null,
    lastUpdated: null
  });

  const fetchStatus = useCallback(async () => {
    if (!executionId || !enabled) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const status = await algorithmsService.getAlgorithmStatus(executionId);
      setState({
        status,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.message || 'Failed to fetch algorithm status'
      }));
    }
  }, [executionId, enabled]);

  useEffect(() => {
    if (!enabled || !executionId) return;

    // Initial fetch
    fetchStatus();

    // Set up polling
    const interval = setInterval(fetchStatus, pollingInterval);

    return () => clearInterval(interval);
  }, [fetchStatus, pollingInterval, enabled, executionId]);

  const refresh = useCallback(() => {
    fetchStatus();
  }, [fetchStatus]);

  return {
    ...state,
    refresh
  };
};

export default useAlgorithmStatus;
