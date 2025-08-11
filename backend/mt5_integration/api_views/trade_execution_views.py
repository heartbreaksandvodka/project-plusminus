from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import AlgorithmExecution, MT5Account
from ..serializers import AlgorithmExecutionSerializer
from ..mt5_service import MT5AlgorithmManager
from ..api_views.mt5_authentication_views import get_mt5_account
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ALGORITHMSMT5EA')))
from risk_manager import RiskManager

# API to start an algorithm on the user's MT5 account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_algorithm(request):
    """Start an algorithm on user's MT5 account"""
    algorithm_name = request.data.get('algorithm_name')
    symbol = request.data.get('symbol', '')
    if not algorithm_name:
        return Response({'error': 'Algorithm name is required'}, status=400)
    account, error = get_mt5_account(request.user)
    if error:
        return Response(error, status=400)
    try:
        # Start the EA script as a subprocess
        result = MT5AlgorithmManager.start_algorithm(account, algorithm_name, symbol)
        if result['status'] == 'success':
            execution = AlgorithmExecution.objects.create(
                mt5_account=account,
                algorithm_name=algorithm_name,
                execution_status='running',
                pid=result.get('pid')
            )

            # Fetch risk management details
            risk_manager = RiskManager()
            risk_details = {
                'max_risk_percent': risk_manager.max_risk_percent,
                'current_risk': risk_manager.calculate_current_risk(account)
            }

            return Response({
                'message': result['message'],
                'execution': AlgorithmExecutionSerializer(execution).data,
                'risk_management': risk_details
            }, status=201)
        else:
            return Response(result, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# API to stop a running algorithm on the user's MT5 account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_algorithm(request, execution_id):
    """Stop a running algorithm"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        if execution.pid is None:
            return Response({'error': 'No PID found for this execution.'}, status=400)
        result = MT5AlgorithmManager.stop_algorithm(execution.pid)
        if result['status'] == 'success':
            execution.execution_status = 'stopped'
            execution.save()
            return Response({'message': result['message'], 'execution': AlgorithmExecutionSerializer(execution).data}, status=200)
        else:
            return Response(result, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# API to pause a running algorithm on the user's MT5 account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_algorithm(request, execution_id):
    """Pause a running algorithm"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        if execution.execution_status != 'running':
            return Response({'error': 'Algorithm is not running and cannot be paused.'}, status=400)
        if execution.pid is None:
            return Response({'error': 'No PID found for this execution.'}, status=400)
        algorithm_name = request.data.get('algorithm_name', execution.algorithm_name)
        result = MT5AlgorithmManager.pause_algorithm(execution.pid, algorithm_name=algorithm_name)
        if result['status'] == 'success':
            execution.execution_status = 'paused'
            execution.save()
            return Response({'message': 'Algorithm paused successfully.', 'execution': execution.id}, status=200)
        else:
            return Response(result, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# API to resume a paused algorithm on the user's MT5 account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_algorithm(request, execution_id):
    """Resume a paused algorithm"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        if execution.execution_status != 'paused':
            return Response({'error': 'Algorithm is not paused and cannot be resumed.'}, status=400)
        if execution.pid is None:
            return Response({'error': 'No PID found for this execution.'}, status=400)
        algorithm_name = request.data.get('algorithm_name', execution.algorithm_name)
        result = MT5AlgorithmManager.resume_algorithm(execution.pid, algorithm_name=algorithm_name)
        if result['status'] == 'success':
            execution.execution_status = 'running'
            execution.save()
            return Response({'message': 'Algorithm resumed successfully.', 'execution': execution.id}, status=200)
        else:
            return Response(result, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
