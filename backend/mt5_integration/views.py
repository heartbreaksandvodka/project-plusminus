from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
