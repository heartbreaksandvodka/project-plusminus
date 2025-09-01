from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account, AlgorithmExecution
from datetime import datetime, timezone, timedelta
import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def real_time_profitability(request):
    """Return real-time profitability data from MT5 account including balance-equity difference."""
    try:
        # Get user's MT5 account
        try:
            account = MT5Account.objects.get(user=request.user)
        except MT5Account.DoesNotExist:
            return Response({"error": "No MT5 account found"}, status=404)
        
        if not mt5.initialize():
            return Response({"error": "Failed to initialize MT5"}, status=500)
        
        try:
            # Login to MT5 account
            password = account.get_password()
            authorized = mt5.login(login=int(account.account_number), password=password, server=account.server)
            if not authorized:
                return Response({"error": "Failed to login to MT5 account"}, status=401)
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                return Response({"error": "Failed to get account info"}, status=500)
            
            # Get positions for open positions count
            positions = mt5.positions_get()
            open_positions_count = len(positions) if positions else 0
            
            # Calculate profit/loss as difference between balance and equity
            balance = float(account_info.balance)
            equity = float(account_info.equity)
            profit_loss = equity - balance  # This represents unrealized P&L
            
            # Get historical data for profitability calculation
            date_to = datetime.now()
            date_from = date_to - timedelta(days=365)  # Get last year of data
            
            # Get deals history to calculate initial balance and deposits/withdrawals
            deals = mt5.history_deals_get(date_from, date_to)
            
            # Calculate historical data
            initial_balance = balance
            total_deposits = 0
            total_withdrawals = 0
            trading_days = 30  # Default, could be calculated from actual trading history
            
            if deals:
                # Find earliest deal to estimate start date
                earliest_deal = min(deals, key=lambda d: d.time)
                start_date = datetime.fromtimestamp(earliest_deal.time).isoformat()
                
                # Calculate deposits/withdrawals (deals with type 2 are balance operations)
                for deal in deals:
                    if hasattr(deal, 'type') and deal.type == 2:  # Balance operation
                        if deal.profit > 0:
                            total_deposits += deal.profit
                        else:
                            total_withdrawals += abs(deal.profit)
                
                # Calculate trading days
                trading_days = max(1, (date_to - datetime.fromtimestamp(earliest_deal.time)).days)
            else:
                start_date = (date_to - timedelta(days=30)).isoformat()
            
            # Get EA statistics
            executions = AlgorithmExecution.objects.filter(mt5_account=account)
            ea_total_profit = sum(float(exe.profit_loss) for exe in executions)
            ea_total_loss = sum(float(exe.profit_loss) for exe in executions if float(exe.profit_loss) < 0)
            ea_total_trades = sum(exe.trades_count for exe in executions)
            ea_wins = sum(1 for exe in executions if float(exe.profit_loss) > 0)
            ea_win_rate = (ea_wins / len(executions) * 100) if executions else 0
            
            # Calculate max drawdown (simplified - would need more detailed calculation)
            max_drawdown = 0  # This would require more complex calculation from history
            
            response_data = {
                "account_data": {
                    "balance": balance,
                    "equity": equity,
                    "profit_loss": profit_loss,
                    "margin": float(account_info.margin),
                    "margin_free": float(account_info.margin_free),
                    "margin_level": float(account_info.margin_level) if account_info.margin_level else 0,
                    "open_positions": open_positions_count,
                    "account_currency": account_info.currency,
                    "last_updated": datetime.now().isoformat()
                },
                "historical_data": {
                    "initial_balance": initial_balance,
                    "total_deposits": total_deposits,
                    "total_withdrawals": total_withdrawals,
                    "trading_days": trading_days,
                    "start_date": start_date
                },
                "ea_statistics": {
                    "total_trades": ea_total_trades,
                    "total_profit": ea_total_profit,
                    "total_loss": abs(ea_total_loss),
                    "win_rate": round(ea_win_rate, 2),
                    "max_drawdown": max_drawdown
                }
            }
            
            # Update account status to connected on successful data fetch
            account.connection_status = 'connected'
            account.last_connected = datetime.now()
            account.balance = balance
            account.equity = equity
            account.margin = account_info.margin
            account.save()
            
            return Response(response_data, status=200)
            
        finally:
            mt5.shutdown()
            
    except Exception as e:
        logger.error(f"Real-time profitability error: {str(e)}")
        return Response({"error": f"Failed to get real-time data: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_profitability(request):
    """Force refresh MT5 account status and return updated profitability data."""
    return real_time_profitability(request)
