from rest_framework import serializers
from .models import MT5Account, MT5TradingSession, AlgorithmExecution, TradeResult, AlgorithmSignal


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
    recent_trades_count = serializers.SerializerMethodField()
    performance_summary = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AlgorithmExecution
        fields = '__all__'
        read_only_fields = ['mt5_account', 'started_at']
    
    def get_recent_trades_count(self, obj):
        """Get count of trades in last 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(hours=24)
        return obj.trade_results.filter(opened_at__gte=yesterday).count()
    
    def get_performance_summary(self, obj):
        """Get basic performance metrics"""
        all_trades = obj.trade_results.filter(trade_status='closed')
        if not all_trades.exists():
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0
            }
        
        total_trades = all_trades.count()
        winning_trades = all_trades.filter(profit_loss__gt=0).count()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(trade.profit_loss for trade in all_trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': float(total_pnl)
        }
    
    def get_status_display(self, obj):
        """Get human-readable status"""
        status_map = {
            'pending': 'Pending Start',
            'running': 'Running',
            'paused': 'Paused',
            'stopped': 'Stopped',
            'error': 'Error',
            'completed': 'Completed'
        }
        return status_map.get(obj.execution_status, obj.execution_status)


class TradeResultSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()
    profit_loss_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = TradeResult
        fields = '__all__'
        read_only_fields = ['algorithm_execution']
    
    def get_duration_display(self, obj):
        """Get formatted duration"""
        if obj.duration_seconds:
            hours = obj.duration_seconds // 3600
            minutes = (obj.duration_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "N/A"
    
    def get_profit_loss_formatted(self, obj):
        """Get formatted P&L with currency"""
        if obj.profit_loss:
            sign = "+" if obj.profit_loss > 0 else ""
            return f"{sign}{obj.profit_loss:.2f}"
        return "0.00"


class AlgorithmSignalSerializer(serializers.ModelSerializer):
    age_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AlgorithmSignal
        fields = '__all__'
        read_only_fields = ['algorithm_execution']
    
    def get_age_display(self, obj):
        """Get human-readable age of signal"""
        from django.utils import timezone
        age = timezone.now() - obj.generated_at
        
        if age.days > 0:
            return f"{age.days}d ago"
        elif age.seconds >= 3600:
            hours = age.seconds // 3600
            return f"{hours}h ago"
        elif age.seconds >= 60:
            minutes = age.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"


class AlgorithmExecutionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new algorithm executions"""
    class Meta:
        model = AlgorithmExecution
        fields = [
            'algorithm_name', 'algorithm_type', 'parameters', 
            'symbol', 'timeframe', 'initial_balance'
        ]
    
    def validate_parameters(self, value):
        """Validate algorithm parameters"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a valid JSON object")
        
        # Basic parameter validation
        required_params = ['lot_size', 'max_positions']
        for param in required_params:
            if param not in value:
                raise serializers.ValidationError(f"Missing required parameter: {param}")
        
        return value


class TradeResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trade results from EA"""
    class Meta:
        model = TradeResult
        fields = [
            'ticket', 'symbol', 'trade_type', 'volume', 'open_price',
            'close_price', 'stop_loss', 'take_profit', 'profit_loss',
            'commission', 'swap', 'comment', 'opened_at', 'closed_at',
            'trade_status'
        ]


class AlgorithmSignalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating algorithm signals"""
    class Meta:
        model = AlgorithmSignal
        fields = [
            'signal_type', 'symbol', 'action', 'confidence', 'price',
            'stop_loss', 'take_profit', 'volume', 'reasoning'
        ]


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
