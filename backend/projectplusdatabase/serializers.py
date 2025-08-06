from rest_framework import serializers
from .models import EATemplate, UserEAInstance, EAPerformance

class EATemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EATemplate
        fields = '__all__'

class UserEAInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEAInstance
        fields = '__all__'

class EAPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EAPerformance
        fields = '__all__'
