from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account
from datetime import datetime, timedelta
from collections import defaultdict
import MetaTrader5 as mt5

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manual_statistics(request):
    """Return live manual trading statistics for the authenticated user's MT5 account."""
    try:
        account = MT5Account.objects.get(user=request.user)
        password = account.get_password()
        if not mt5.initialize():
            return Response({"error": "Failed to initialize MetaTrader 5", "details": mt5.last_error()}, status=500)
        authorized = mt5.login(login=int(account.account_number), password=password, server=account.server)
        if not authorized:
            err = mt5.last_error()
            mt5.shutdown()
            return Response({"error": "MT5 login failed", "details": err}, status=401)

        positions = mt5.positions_get()
        orders = mt5.orders_get()
        date_to = datetime.now()
        date_from = date_to - timedelta(days=365)
        history_deals = mt5.history_deals_get(date_from, date_to)

        manual_deals = [d for d in history_deals or [] if getattr(d, 'magic', 0) == 0]
        total_trades = len(manual_deals)
        total_profit = sum(getattr(d, 'profit', 0) for d in manual_deals)
        wins = sum(1 for d in manual_deals if getattr(d, 'profit', 0) > 0)
        win_rate = (wins / total_trades * 100) if total_trades else 0
        initial_balance = float(account.balance) - total_profit if account.balance is not None else 0
        profitability_percent = (total_profit / initial_balance * 100) if initial_balance else 0

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

        mt5.shutdown()
        return Response({
            "total_trades": total_trades,
            "profitability_percent": round(profitability_percent, 2),
            "win_rate": round(win_rate, 2),
            "sessions": session_list
        }, status=200)
    except MT5Account.DoesNotExist:
        return Response({"error": "No MT5 account found"}, status=404)
    except Exception as e:
        try:
            mt5.shutdown()
        except:
            pass
        return Response({"error": str(e)}, status=500)
