from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account
from ..mt5_service import MT5ConnectionManager
from ..mt5_auto_manager import MT5AutoManager
from ..serializers import MT5AccountConnectionSerializer, MT5AccountStatusSerializer

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
            }, status=200)
        else:
            return Response({
                'status': 'error',
                'message': 'Connection test failed',
                'error': result
            }, status=400)
    return Response(serializer.errors, status=400)

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
        }, status=200)
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found',
            'message': 'Please set up your MT5 account first.'
        }, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mt5_setup_status(request):
    """Get MT5 terminal status and setup guidance"""
    try:
        status = MT5AutoManager.get_status()
        
        # Add setup recommendations
        recommendations = []
        
        if not status['mt5_executable_found']:
            recommendations.append({
                'priority': 'high',
                'action': 'Install MetaTrader 5',
                'description': 'MT5 terminal not found. Please download and install from your broker.',
                'url': 'https://www.exness.com/trading-platforms/metatrader5/'
            })
        
        if not status['mt5_terminal_running']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Start MT5 Terminal',
                'description': 'MT5 terminal is not running. You can try auto-start or open manually.'
            })
        
        if not status['logged_in']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Login Required',
                'description': 'MT5 terminal needs to be logged in with your trading account.'
            })
        
        return Response({
            'status': status,
            'recommendations': recommendations,
            'automation_available': status['mt5_executable_found'],
            'ready_for_trading': status['logged_in']
        }, status=200)
        
    except Exception as e:
        return Response({
            'error': 'Failed to check MT5 status',
            'details': str(e)
        }, status=500)
