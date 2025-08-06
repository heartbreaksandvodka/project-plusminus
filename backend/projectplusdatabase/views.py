from rest_framework import viewsets
from .models import EATemplate, UserEAInstance, EAPerformance
from .serializers import EATemplateSerializer, UserEAInstanceSerializer, EAPerformanceSerializer
from rest_framework.permissions import IsAuthenticated

class EATemplateViewSet(viewsets.ModelViewSet):
    queryset = EATemplate.objects.all()
    serializer_class = EATemplateSerializer
    permission_classes = [IsAuthenticated]

class UserEAInstanceViewSet(viewsets.ModelViewSet):
    queryset = UserEAInstance.objects.all()
    serializer_class = UserEAInstanceSerializer
    permission_classes = [IsAuthenticated]

class EAPerformanceViewSet(viewsets.ModelViewSet):
    queryset = EAPerformance.objects.all()
    serializer_class = EAPerformanceSerializer
    permission_classes = [IsAuthenticated]
