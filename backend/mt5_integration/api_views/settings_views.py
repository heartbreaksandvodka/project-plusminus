from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Mock settings data for demonstration purposes
MOCK_SETTINGS = {
    "notifications": True,
    "theme": "light",
    "privacy": "public",
}

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    if request.method == 'GET':
        # Return the mock settings
        return Response(MOCK_SETTINGS, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the mock settings with the provided data
        data = request.data
        MOCK_SETTINGS.update(data)
        return Response(MOCK_SETTINGS, status=status.HTTP_200_OK)
