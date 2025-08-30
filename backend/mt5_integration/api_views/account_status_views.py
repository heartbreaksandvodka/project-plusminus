from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account, AlgorithmExecution
from ..serializers import MT5AccountStatusSerializer, AlgorithmExecutionSerializer
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import MetaTrader5 as mt5

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_statistics(request):
    """Return comprehensive account statistics including EA and manual trading data."""
    try:
        account = MT5Account.objects.get(user=request.user)
        executions = AlgorithmExecution.objects.filter(mt5_account=account)
        now = datetime.now(timezone.utc)

        # EA STATISTICS
        # EA activity durations
        ea_activity = []
        for exe in executions:
            if exe.execution_status == 'running':
                start = exe.started_at
                duration = now - start
                days = duration.days
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"
                ea_activity.append({
                    "ea_name": exe.algorithm_name,
                    "active_duration": duration_str,
                    "start_time": exe.started_at,
                })

        # EA performance calculations
        ea_total_profit = sum(float(exe.profit_loss) for exe in executions)
        ea_initial_balance = float(account.balance) - ea_total_profit if account.balance is not None else 0
        ea_profitability_percent = (ea_total_profit / ea_initial_balance * 100) if ea_initial_balance else 0
        ea_total_trades = sum(exe.trades_count for exe in executions)
        ea_wins = sum(1 for exe in executions if float(exe.profit_loss) > 0)
        ea_win_rate = (ea_wins / len(executions) * 100) if executions else 0
        running_eas = executions.filter(execution_status='running').count()

        # MANUAL TRADING STATISTICS
        manual_stats = {
            "total_trades": 0,
            "profitability_percent": 0,
            "win_rate": 0,
            "sessions": []
        }

        try:
            # Get manual trading data from MT5
            password = account.get_password()
            if mt5.initialize():
                authorized = mt5.login(login=int(account.account_number), password=password, server=account.server)
                if authorized:
                    date_to = datetime.now()
                    date_from = date_to - timedelta(days=365)
                    history_deals = mt5.history_deals_get(date_from, date_to)
                    
                    # Filter manual deals (magic number = 0)
                    manual_deals = [d for d in history_deals or [] if getattr(d, 'magic', 0) == 0]
                    manual_total_trades = len(manual_deals)
                    manual_total_profit = sum(getattr(d, 'profit', 0) for d in manual_deals)
                    manual_wins = sum(1 for d in manual_deals if getattr(d, 'profit', 0) > 0)
                    manual_win_rate = (manual_wins / manual_total_trades * 100) if manual_total_trades else 0
                    manual_initial_balance = float(account.balance) - manual_total_profit if account.balance is not None else 0
                    manual_profitability_percent = (manual_total_profit / manual_initial_balance * 100) if manual_initial_balance else 0

                    # Group deals by session (by day)
                    sessions = defaultdict(lambda: {"trades_executed": 0, "profit_loss": 0, "session_start": None, "session_end": None})
                    for d in manual_deals:
                        dt = getattr(d, 'time', None)
                        if dt:
                            day = datetime.fromtimestamp(dt).date()
                            s = sessions[day]
                            s["trades_executed"] += 1
                            s["profit_loss"] += getattr(d, 'profit', 0)
                            if not s["session_start"] or dt < s["session_start"]:
                                s["session_start"] = dt
                            if not s["session_end"] or dt > s["session_end"]:
                                s["session_end"] = dt

                    session_list = []
                    for day, s in sessions.items():
                        session_list.append({
                            "session_start": datetime.fromtimestamp(s["session_start"]).isoformat() if s["session_start"] else None,
                            "session_end": datetime.fromtimestamp(s["session_end"]).isoformat() if s["session_end"] else None,
                            "trades_executed": s["trades_executed"],
                            "profit_loss": s["profit_loss"],
                        })

                    manual_stats = {
                        "total_trades": manual_total_trades,
                        "profitability_percent": round(manual_profitability_percent, 2),
                        "win_rate": round(manual_win_rate, 2),
                        "sessions": session_list
                    }
                mt5.shutdown()
        except Exception as e:
            # If manual data fails, continue with empty manual stats
            pass

        return Response({
            # EA Statistics
            "ea_activity": ea_activity,
            "ea_profitability_percent": round(ea_profitability_percent, 2),
            "ea_total_trades": ea_total_trades,
            "ea_win_rate": round(ea_win_rate, 2),
            "running_eas": running_eas,
            
            # Manual Trading Statistics
            "manual_stats": manual_stats,
            
            # Combined/Legacy fields for backward compatibility
            "profitability_percent": round(ea_profitability_percent, 2),
            "total_trades": ea_total_trades,
            "win_rate": round(ea_win_rate, 2)
        }, status=200)
    except MT5Account.DoesNotExist:
        return Response({"error": "No MT5 account found"}, status=404)
