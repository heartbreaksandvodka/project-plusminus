from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account
from ..mt5_service import MT5ConnectionManager
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
