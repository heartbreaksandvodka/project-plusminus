from .mt5_service import MT5ConnectionManager

# --- NEW: Live Manual Trading Statistics Endpoint ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import MetaTrader5 as mt5

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manual_statistics(request):
    """Return live manual trading statistics for the authenticated user's MT5 account."""
    try:
        account = MT5Account.objects.get(user=request.user)
        password = account.get_password()
        # Connect to MT5
        if not mt5.initialize():
            return Response({"error": "Failed to initialize MetaTrader 5", "details": mt5.last_error()}, status=500)
        authorized = mt5.login(login=int(account.account_number), password=password, server=account.server)
        if not authorized:
            err = mt5.last_error()
            mt5.shutdown()
            return Response({"error": "MT5 login failed", "details": err}, status=401)

        # Fetch all positions and orders (manual trades have magic=0)
        positions = mt5.positions_get()
        orders = mt5.orders_get()
        from datetime import timedelta
        date_to = datetime.now()
        date_from = date_to - timedelta(days=365)
        history_deals = mt5.history_deals_get(date_from, date_to)

        # Filter manual trades (magic=0)
        manual_positions = [p for p in positions or [] if getattr(p, 'magic', 0) == 0]
        manual_orders = [o for o in orders or [] if getattr(o, 'magic', 0) == 0]
        manual_deals = [d for d in history_deals or [] if getattr(d, 'magic', 0) == 0]

        # Calculate stats
        total_trades = len(manual_deals)
        total_profit = sum(getattr(d, 'profit', 0) for d in manual_deals)
        wins = sum(1 for d in manual_deals if getattr(d, 'profit', 0) > 0)
        win_rate = (wins / total_trades * 100) if total_trades else 0
        # Profitability: relative to account balance
        initial_balance = float(account.balance) - total_profit if account.balance is not None else 0
        profitability_percent = (total_profit / initial_balance * 100) if initial_balance else 0

        # Sessions: group by day
        from collections import defaultdict
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

from datetime import datetime, timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MT5Account, AlgorithmExecution
from .serializers import (
    MT5AccountSerializer, 
    MT5AccountConnectionSerializer,
    MT5AccountStatusSerializer,
    AlgorithmExecutionSerializer
)
from .mt5_service import MT5ConnectionManager, MT5AlgorithmManager
import logging

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_statistics(request):
    """Return dynamic account statistics for the authenticated user."""
    try:
        account = MT5Account.objects.get(user=request.user)
        executions = AlgorithmExecution.objects.filter(mt5_account=account)
        # For non-EA/manual trades, assume they are tracked in MT5TradingSession
        from .models import MT5TradingSession
        manual_sessions = MT5TradingSession.objects.filter(mt5_account=account)
        now = datetime.now(timezone.utc)

        # EA activity durations
        ea_activity = []
        for exe in executions:
            if exe.execution_status == 'running':
                start = exe.started_at
                duration = now - start
                # Format duration as days, hours, minutes
                days = duration.days
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"
                ea_activity.append({
                    "ea_name": exe.algorithm_name,
                    "active_duration": duration_str,
                    "start_time": exe.started_at,
                })

        # Profitability: (sum of profit_loss) / (sum of initial balance or abs min balance)
        total_profit = sum(float(exe.profit_loss) for exe in executions)
        # Use account.balance as current, estimate initial as balance - total_profit
        initial_balance = float(account.balance) - total_profit if account.balance is not None else 0
        profitability_percent = (total_profit / initial_balance * 100) if initial_balance else 0

        # Total trades and win rate
        total_trades = sum(exe.trades_count for exe in executions)
        wins = sum(1 for exe in executions if float(exe.profit_loss) > 0)
        win_rate = (wins / len(executions) * 100) if executions else 0

        # Number of running EAs
        running_eas = executions.filter(execution_status='running').count()

        # Manual/non-EA stats
        manual_total_trades = sum(s.trades_executed for s in manual_sessions)
        manual_total_profit = sum(float(s.profit_loss) for s in manual_sessions)
        manual_win_sessions = sum(1 for s in manual_sessions if float(s.profit_loss) > 0)
        manual_win_rate = (manual_win_sessions / len(manual_sessions) * 100) if manual_sessions else 0
        manual_profitability_percent = 0
        if manual_sessions:
            # Estimate initial balance for manual as current - total manual profit
            manual_initial_balance = float(account.balance) - manual_total_profit if account.balance is not None else 0
            manual_profitability_percent = (manual_total_profit / manual_initial_balance * 100) if manual_initial_balance else 0

        return Response({
            "ea_activity": ea_activity,
            "profitability_percent": round(profitability_percent, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "running_eas": running_eas,
            "manual_stats": {
                "total_trades": manual_total_trades,
                "profitability_percent": round(manual_profitability_percent, 2),
                "win_rate": round(manual_win_rate, 2),
                "sessions": [
                    {
                        "session_start": s.session_start,
                        "session_end": s.session_end,
                        "trades_executed": s.trades_executed,
                        "profit_loss": float(s.profit_loss),
                    } for s in manual_sessions
                ]
            }
        }, status=status.HTTP_200_OK)
    except MT5Account.DoesNotExist:
        return Response({"error": "No MT5 account found"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MT5Account, AlgorithmExecution
from .serializers import (
    MT5AccountSerializer, 
    MT5AccountConnectionSerializer,
    MT5AccountStatusSerializer,
    AlgorithmExecutionSerializer
)
from .mt5_service import MT5ConnectionManager, MT5AlgorithmManager
import logging


logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mt5_account(request):
    """
    GET: Retrieve user's MT5 account
    POST: Create or update MT5 account
    """
    if request.method == 'GET':
        try:
            account = MT5Account.objects.get(user=request.user)
            serializer = MT5AccountStatusSerializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MT5Account.DoesNotExist:
            return Response({
                'error': 'No MT5 account found',
                'message': 'Please set up your MT5 account credentials first.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        try:
            # Check if account already exists
            account = MT5Account.objects.get(user=request.user)
            serializer = MT5AccountSerializer(account, data=request.data, partial=True)
        except MT5Account.DoesNotExist:
            serializer = MT5AccountSerializer(data=request.data)
        
        if serializer.is_valid():
            account = serializer.save(user=request.user)
            
            # Test connection
            if 'password' in request.data:
                connection_result = MT5ConnectionManager.update_account_status(account)
                return Response({
                    'message': 'MT5 account saved successfully',
                    'account': MT5AccountStatusSerializer(account).data,
                    'connection': connection_result
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'MT5 account saved successfully',
                    'account': MT5AccountStatusSerializer(account).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_mt5_connection(request):
    """Test MT5 connection with provided credentials"""
    serializer = MT5AccountConnectionSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        success, result = MT5ConnectionManager.test_connection(
            data['account_number'],
            data['password'],
            data['server']
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Connection test successful',
                'data': result
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Connection test failed',
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_account_status(request):
    """Refresh MT5 account status and balance"""
    try:
        account = MT5Account.objects.get(user=request.user)
        result = MT5ConnectionManager.update_account_status(account)
        
        return Response({
            'message': 'Account status refreshed',
            'account': MT5AccountStatusSerializer(account).data,
            'connection': result
        }, status=status.HTTP_200_OK)
        
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found',
            'message': 'Please set up your MT5 account first.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_mt5_account(request):
    """Delete user's MT5 account"""
    try:
        account = MT5Account.objects.get(user=request.user)
        account.delete()
        
        return Response({
            'message': 'MT5 account deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def algorithm_executions(request):
    """Get user's algorithm executions"""
    try:
        account = MT5Account.objects.get(user=request.user)
        executions = AlgorithmExecution.objects.filter(mt5_account=account)
        serializer = AlgorithmExecutionSerializer(executions, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found',
            'message': 'Please set up your MT5 account first.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_algorithm(request):
    """Start an algorithm on user's MT5 account"""
    algorithm_name = request.data.get('algorithm_name')
    
    if not algorithm_name:
        return Response({
            'error': 'Algorithm name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        account = MT5Account.objects.get(user=request.user)
        
        if not account.is_connected:
            return Response({
                'error': 'MT5 account not connected',
                'message': 'Please ensure your MT5 account is connected before starting algorithms.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = MT5AlgorithmManager.start_algorithm(account, algorithm_name)
        
        if result['status'] == 'success':
            # Create algorithm execution record
            execution = AlgorithmExecution.objects.create(
                mt5_account=account,
                algorithm_name=algorithm_name,
                execution_status='running'
            )
            
            return Response({
                'message': result['message'],
                'execution': AlgorithmExecutionSerializer(execution).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found',
            'message': 'Please set up your MT5 account first.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_algorithm(request, execution_id):
    """Stop a running algorithm"""
    try:
        account = MT5Account.objects.get(user=request.user)
        execution = get_object_or_404(
            AlgorithmExecution, 
            id=execution_id, 
            mt5_account=account
        )
        
        result = MT5AlgorithmManager.stop_algorithm(str(execution_id))
        
        if result['status'] == 'success':
            execution.execution_status = 'stopped'
            execution.save()
            
            return Response({
                'message': result['message'],
                'execution': AlgorithmExecutionSerializer(execution).data
            }, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found'
        }, status=status.HTTP_404_NOT_FOUND)
