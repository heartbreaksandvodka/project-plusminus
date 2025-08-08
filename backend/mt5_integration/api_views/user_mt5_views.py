from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account
from ..serializers import MT5AccountStatusSerializer

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_mt5_account(request):
    """Delete user's MT5 account"""
    try:
        account = MT5Account.objects.get(user=request.user)
        account.delete()
        return Response({
            'message': 'MT5 account deleted successfully'
        }, status=200)
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found'
        }, status=404)
