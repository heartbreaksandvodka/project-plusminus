from rest_framework.routers import DefaultRouter
from .views import EATemplateViewSet, UserEAInstanceViewSet, EAPerformanceViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'eatemplates', EATemplateViewSet)
router.register(r'usereainstances', UserEAInstanceViewSet)
router.register(r'eaperformance', EAPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
