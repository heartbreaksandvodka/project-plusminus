export interface MT5Account {
  id: number;
  account_number: string;
  masked_account_number: string;
  broker_name: string;
  server: string;
  account_type: 'demo' | 'real';
  connection_status: 'connected' | 'disconnected' | 'error' | 'pending';
  last_connected: string | null;
  balance: number | null;
  equity: number | null;
  margin: number | null;
  currency: string;
  is_connected: boolean;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface MT5AccountForm {
  account_number: string;
  broker_name: string;
  server: string;
  password: string;
  account_type: 'demo' | 'real';
}

export interface MT5ConnectionTest {
  account_number: string;
  broker_name: string;
  server: string;
  password: string;
  account_type: 'demo' | 'real';
}

export interface AlgorithmExecution {
  id: number;
  algorithm_name: string;
  execution_status: 'running' | 'stopped' | 'paused' | 'error' | 'completed';
  started_at: string;
  stopped_at: string | null;
  profit_loss: number;
  trades_count: number;
  error_message: string | null;
  last_heartbeat: string | null;
}
