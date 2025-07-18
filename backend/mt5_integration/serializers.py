from rest_framework import serializers
from .models import MT5Account, MT5TradingSession, AlgorithmExecution


class MT5AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    masked_account_number = serializers.ReadOnlyField()
    is_connected = serializers.ReadOnlyField()
    
    class Meta:
        model = MT5Account
        fields = [
            'id', 'account_number', 'masked_account_number', 'broker_name', 
            'server', 'account_type', 'connection_status', 'last_connected',
            'balance', 'equity', 'margin', 'currency', 'is_connected',
            'password', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['connection_status', 'last_connected', 'balance', 'equity', 'margin']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        account = MT5Account.objects.create(**validated_data)
        if password:
            account.set_password(password)
            account.save()
        return account
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MT5AccountConnectionSerializer(serializers.Serializer):
    """Serializer for testing MT5 connection"""
    account_number = serializers.CharField(max_length=20)
    broker_name = serializers.CharField(max_length=100)
    server = serializers.CharField(max_length=100)
    password = serializers.CharField()
    account_type = serializers.ChoiceField(choices=MT5Account.ACCOUNT_TYPES, default='demo')


class MT5TradingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MT5TradingSession
        fields = '__all__'
        read_only_fields = ['mt5_account', 'session_start']


class AlgorithmExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmExecution
        fields = '__all__'
        read_only_fields = ['mt5_account', 'started_at']


class MT5AccountStatusSerializer(serializers.ModelSerializer):
    """Simplified serializer for account status display"""
    masked_account_number = serializers.ReadOnlyField()
    is_connected = serializers.ReadOnlyField()
    
    class Meta:
        model = MT5Account
        fields = [
            'id', 'masked_account_number', 'broker_name', 'account_type',
            'connection_status', 'last_connected', 'balance', 'equity',
            'margin', 'currency', 'is_connected'
        ]
