// Profitability calculation utility
export interface ProfitabilityData {
  // Core Balance Data
  initial_balance: number;
  current_balance: number;
  realized_pnl: number;
  unrealized_pnl: number;
  
  // Transaction Data
  total_deposits: number;
  total_withdrawals: number;
  
  // Trade Statistics
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  total_profit: number;
  total_loss: number;
  
  // Risk Metrics
  max_drawdown: number;
  max_consecutive_losses: number;
  
  // Time-based
  trading_days: number;
  start_date: string;
}

export interface ProfitabilityResult {
  total_profitability: number;
  realized_profitability: number;
  unrealized_profitability: number;
  daily_average: number;
  win_rate: number;
  profit_factor: number;
  sharpe_ratio: number;
  max_drawdown_percent: number;
  average_trade: number;
}

export class ProfitabilityCalculator {
  
  /**
   * Calculate comprehensive profitability metrics
   * Using Total Return method including unrealized P&L
   */
  static calculateProfitability(data: ProfitabilityData): ProfitabilityResult {
    // Prevent division by zero
    const safeAdjustedBase = Math.max(
      data.initial_balance + data.total_deposits - data.total_withdrawals,
      1
    );
    
    // Net equity change (realized only)
    const realizedEquityChange = data.current_balance - data.initial_balance;
    
    // Realized profitability (without unrealized P&L)
    const realizedProfitability = (realizedEquityChange / safeAdjustedBase) * 100;
    
    // Unrealized profitability component
    const unrealizedProfitability = (data.unrealized_pnl / safeAdjustedBase) * 100;
    
    // Total profitability (including unrealized P&L)
    const totalProfitability = realizedProfitability + unrealizedProfitability;
    
    // Daily average (if trading days > 0)
    const dailyAverage = data.trading_days > 0 
      ? totalProfitability / data.trading_days 
      : 0;
    
    // Win rate
    const winRate = data.total_trades > 0 
      ? (data.winning_trades / data.total_trades) * 100 
      : 0;
    
    // Profit factor (total profit / total loss)
    const profitFactor = Math.abs(data.total_loss) > 0 
      ? data.total_profit / Math.abs(data.total_loss) 
      : data.total_profit > 0 ? Infinity : 0;
    
    // Sharpe ratio (simplified: excess return / volatility)
    // Using max drawdown as volatility proxy
    const sharpeRatio = data.max_drawdown > 0 
      ? totalProfitability / data.max_drawdown 
      : totalProfitability;
    
    // Max drawdown percentage
    const maxDrawdownPercent = (data.max_drawdown / safeAdjustedBase) * 100;
    
    // Average trade P&L
    const averageTrade = data.total_trades > 0 
      ? data.realized_pnl / data.total_trades 
      : 0;
    
    return {
      total_profitability: Number(totalProfitability.toFixed(2)),
      realized_profitability: Number(realizedProfitability.toFixed(2)),
      unrealized_profitability: Number(unrealizedProfitability.toFixed(2)),
      daily_average: Number(dailyAverage.toFixed(3)),
      win_rate: Number(winRate.toFixed(1)),
      profit_factor: Number(profitFactor.toFixed(2)),
      sharpe_ratio: Number(sharpeRatio.toFixed(2)),
      max_drawdown_percent: Number(maxDrawdownPercent.toFixed(2)),
      average_trade: Number(averageTrade.toFixed(2))
    };
  }
  
  /**
   * Calculate EA-specific profitability
   */
  static calculateEAProfitability(eaData: any): number {
    if (!eaData || !eaData.trades || eaData.trades.length === 0) {
      return 0;
    }
    
    const totalPnL = eaData.trades.reduce((sum: number, trade: any) => {
      return sum + (trade.profit || 0);
    }, 0);
    
    const initialBalance = eaData.initial_balance || 10000; // Default if not provided
    
    return Number(((totalPnL / initialBalance) * 100).toFixed(2));
  }
  
  /**
   * Calculate time-based profitability
   */
  static calculateTimePeriodProfitability(
    data: ProfitabilityData, 
    days: number
  ): number {
    if (data.trading_days <= 0 || days <= 0) return 0;
    
    const dailyRate = data.realized_pnl / data.trading_days;
    const periodPnL = dailyRate * days;
    const adjustedBase = data.initial_balance + data.total_deposits - data.total_withdrawals;
    
    return Number(((periodPnL / adjustedBase) * 100).toFixed(2));
  }
  
  /**
   * Format profitability for display
   */
  static formatProfitability(value: number): string {
    if (value === 0) return '0.00%';
    if (value > 999.9) return '>999.9%';
    if (value < -99.9) return '<-99.9%';
    
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  }
  
  /**
   * Get profitability status color
   */
  static getProfitabilityColor(value: number): string {
    if (value > 10) return '#22c55e'; // Green for high profit
    if (value > 0) return '#84cc16';  // Light green for profit
    if (value === 0) return '#6b7280'; // Gray for neutral
    if (value > -10) return '#f59e0b'; // Orange for small loss
    return '#ef4444'; // Red for significant loss
  }
}
