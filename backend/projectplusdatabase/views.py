
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import EATemplate, UserEAInstance, EAPerformance
from .serializers import EATemplateSerializer, UserEAInstanceSerializer, EAPerformanceSerializer

class BaseAuthenticatedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

class EATemplateViewSet(BaseAuthenticatedModelViewSet):
    queryset = EATemplate.objects.all()
    serializer_class = EATemplateSerializer

class UserEAInstanceViewSet(BaseAuthenticatedModelViewSet):
    queryset = UserEAInstance.objects.all()
    serializer_class = UserEAInstanceSerializer

class EAPerformanceViewSet(BaseAuthenticatedModelViewSet):
    queryset = EAPerformance.objects.all()
    serializer_class = EAPerformanceSerializer
