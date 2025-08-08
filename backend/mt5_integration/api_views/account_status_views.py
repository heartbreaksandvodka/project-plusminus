from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account, AlgorithmExecution
from ..serializers import MT5AccountStatusSerializer, AlgorithmExecutionSerializer
from datetime import datetime, timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_statistics(request):
    """Return dynamic account statistics for the authenticated user."""
    try:
        account = MT5Account.objects.get(user=request.user)
        executions = AlgorithmExecution.objects.filter(mt5_account=account)
        now = datetime.now(timezone.utc)

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

        total_profit = sum(float(exe.profit_loss) for exe in executions)
        initial_balance = float(account.balance) - total_profit if account.balance is not None else 0
        profitability_percent = (total_profit / initial_balance * 100) if initial_balance else 0

        total_trades = sum(exe.trades_count for exe in executions)
        wins = sum(1 for exe in executions if float(exe.profit_loss) > 0)
        win_rate = (wins / len(executions) * 100) if executions else 0

        running_eas = executions.filter(execution_status='running').count()

        return Response({
            "ea_activity": ea_activity,
            "profitability_percent": round(profitability_percent, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "running_eas": running_eas
        }, status=200)
    except MT5Account.DoesNotExist:
        return Response({"error": "No MT5 account found"}, status=404)
