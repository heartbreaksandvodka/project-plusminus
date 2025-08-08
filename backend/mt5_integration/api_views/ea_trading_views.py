from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import AlgorithmExecution, MT5Account
from ..serializers import AlgorithmExecutionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def algorithm_executions(request):
    """Get user's algorithm executions"""
    try:
        account = MT5Account.objects.get(user=request.user)
        executions = AlgorithmExecution.objects.filter(mt5_account=account)
        serializer = AlgorithmExecutionSerializer(executions, many=True)
        return Response(serializer.data, status=200)
    except MT5Account.DoesNotExist:
        return Response({
            'error': 'No MT5 account found',
            'message': 'Please set up your MT5 account first.'
        }, status=404)
