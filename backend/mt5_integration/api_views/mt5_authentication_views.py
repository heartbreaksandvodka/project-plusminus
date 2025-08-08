from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MT5Account
from ..serializers import MT5AccountSerializer, MT5AccountStatusSerializer
from ..mt5_service import MT5ConnectionManager

def get_mt5_account(user):
    """Reusable function to fetch the MT5 account for a user."""
    try:
        account = MT5Account.objects.get(user=user)
        if not account.is_connected:
            return None, {'error': 'MT5 account not connected'}
        return account, None
    except MT5Account.DoesNotExist:
        return None, {'error': 'No MT5 account found'}

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mt5_account(request):
    """
    GET: Retrieve user's MT5 account
    POST: Create or update MT5 account
    """
    if request.method == 'GET':
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=404)
        serializer = MT5AccountStatusSerializer(account)
        return Response(serializer.data, status=200)
    elif request.method == 'POST':
        try:
            account = MT5Account.objects.get(user=request.user)
            serializer = MT5AccountSerializer(account, data=request.data, partial=True)
        except MT5Account.DoesNotExist:
            serializer = MT5AccountSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save(user=request.user)
            if 'password' in request.data:
                connection_result = MT5ConnectionManager.update_account_status(account)
                return Response({
                    'message': 'MT5 account saved successfully',
                    'account': MT5AccountStatusSerializer(account).data,
                    'connection': connection_result
                }, status=201)
            else:
                return Response({
                    'message': 'MT5 account saved successfully',
                    'account': MT5AccountStatusSerializer(account).data
                }, status=201)
        return Response(serializer.errors, status=400)
