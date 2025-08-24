from django.db import models
from authentication.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import base64


class MT5Account(models.Model):
    ACCOUNT_TYPES = [
        ('demo', 'Demo Account'),
        ('real', 'Real Account'),
    ]
    
    CONNECTION_STATUS = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Connection Error'),
        ('pending', 'Pending Verification'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mt5_account')
    account_number = models.CharField(max_length=20)
    broker_name = models.CharField(max_length=100)
    server = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='demo')
    
    # Encrypted password storage
    encrypted_password = models.TextField()
    
    # Connection status and metadata
    connection_status = models.CharField(max_length=20, choices=CONNECTION_STATUS, default='pending')
    last_connected = models.DateTimeField(null=True, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    equity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'mt5_accounts'
        verbose_name = 'MT5 Account'
        verbose_name_plural = 'MT5 Accounts'
    
    def __str__(self):
        return f"{self.user.email} - {self.account_number} ({self.broker_name})"
    
    def set_password(self, password):
        """Encrypt and store the password"""
        cipher_suite = Fernet(self._get_encryption_key())
        encrypted_password = cipher_suite.encrypt(password.encode())
        self.encrypted_password = base64.urlsafe_b64encode(encrypted_password).decode()
    
    def get_password(self):
        """Decrypt and return the password"""
        cipher_suite = Fernet(self._get_encryption_key())
        encrypted_password = base64.urlsafe_b64decode(self.encrypted_password.encode())
        return cipher_suite.decrypt(encrypted_password).decode()
    
    def _get_encryption_key(self):
        """Generate encryption key from Django secret key"""
        secret_key = settings.SECRET_KEY
        key = base64.urlsafe_b64encode(secret_key[:32].encode().ljust(32, b'0'))
        return key
    
    @property
    def masked_account_number(self):
        """Return masked account number for display"""
        if len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number
    
    @property
    def is_connected(self):
        """Check if account is currently connected"""
        return self.connection_status == 'connected'


class MT5TradingSession(models.Model):
    """Track MT5 trading sessions and activity"""
    mt5_account = models.ForeignKey(MT5Account, on_delete=models.CASCADE, related_name='trading_sessions')
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    
    # Session statistics
    trades_executed = models.IntegerField(default=0)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Session metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'mt5_trading_sessions'
        ordering = ['-session_start']
    
    def __str__(self):
        return f"Session for {self.mt5_account.account_number} - {self.session_start}"


class AlgorithmExecution(models.Model):
    """Track algorithm executions on MT5 accounts"""
    EXECUTION_STATUS = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('paused', 'Paused'),
        ('error', 'Error'),
        ('completed', 'Completed'),
    ]
    
    mt5_account = models.ForeignKey(MT5Account, on_delete=models.CASCADE, related_name='algorithm_executions')
    algorithm_name = models.CharField(max_length=100)
    execution_status = models.CharField(max_length=20, choices=EXECUTION_STATUS, default='running')
    
    # Execution details
    started_at = models.DateTimeField(auto_now_add=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trades_count = models.IntegerField(default=0)
    
    # Process management
    pid = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    # Enhanced tracking fields
    symbol = models.CharField(max_length=20, null=True, blank=True)
    performance_metrics = models.JSONField(default=dict, help_text="Real-time performance data")
    current_positions = models.JSONField(default=list, help_text="Current open positions")
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    current_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Risk management tracking
    risk_violations = models.JSONField(default=list, help_text="Risk rule violations")
    emergency_stops = models.IntegerField(default=0)
    
    # Performance analytics
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_win = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_factor = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Real-time status
    last_trade_time = models.DateTimeField(null=True, blank=True)
    positions_count = models.IntegerField(default=0)
    daily_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'algorithm_executions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.algorithm_name} on {self.mt5_account.account_number}"
    
    def update_performance_metrics(self):
        """Calculate and update performance metrics based on trade results"""
        trades = self.trade_results.all()
        if trades.exists():
            # Calculate win rate
            winning_trades = trades.filter(profit_loss__gt=0).count()
            total_trades = trades.count()
            self.win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            self.winning_trades = winning_trades
            self.losing_trades = total_trades - winning_trades
            
            # Calculate average win/loss
            wins = trades.filter(profit_loss__gt=0)
            losses = trades.filter(profit_loss__lt=0)
            self.avg_win = wins.aggregate(models.Avg('profit_loss'))['profit_loss__avg'] or 0
            self.avg_loss = abs(losses.aggregate(models.Avg('profit_loss'))['profit_loss__avg'] or 0)
            
            # Calculate profit factor
            total_wins = wins.aggregate(models.Sum('profit_loss'))['profit_loss__sum'] or 0
            total_losses = abs(losses.aggregate(models.Sum('profit_loss'))['profit_loss__sum'] or 0)
            self.profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Update total P&L
            self.profit_loss = trades.aggregate(models.Sum('profit_loss'))['profit_loss__sum'] or 0
            self.trades_count = total_trades
            
            self.save()


class TradeResult(models.Model):
    """Track individual trade results for detailed analytics"""
    TRADE_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    TRADE_STATUS = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    
    execution = models.ForeignKey(AlgorithmExecution, on_delete=models.CASCADE, related_name='trade_results')
    
    # Trade identification
    mt5_position_id = models.BigIntegerField(null=True, blank=True, help_text="MT5 position ticket")
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPES)
    symbol = models.CharField(max_length=20)
    volume = models.DecimalField(max_digits=10, decimal_places=3)
    
    # Price levels
    open_price = models.DecimalField(max_digits=15, decimal_places=5)
    close_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    
    # Financial results
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    swap = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timing
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Trade metadata
    trade_status = models.CharField(max_length=10, choices=TRADE_STATUS, default='open')
    signal_data = models.JSONField(default=dict, help_text="Signal generation data")
    exit_reason = models.CharField(max_length=50, null=True, blank=True, help_text="Why trade was closed")
    
    # Performance metrics for this trade
    pips_profit_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    risk_reward_ratio = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trade_results'
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['execution', 'opened_at']),
            models.Index(fields=['symbol', 'opened_at']),
            models.Index(fields=['trade_status']),
        ]
    
    def __str__(self):
        return f"{self.trade_type.upper()} {self.volume} {self.symbol} @ {self.open_price}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if trade is closed
        if self.closed_at and self.opened_at:
            duration = self.closed_at - self.opened_at
            self.duration_seconds = int(duration.total_seconds())
        
        # Calculate pips profit/loss (approximate for major pairs)
        if self.close_price and self.open_price:
            pip_value = 0.0001 if 'JPY' not in self.symbol else 0.01
            if self.trade_type == 'buy':
                pips = (self.close_price - self.open_price) / pip_value
            else:
                pips = (self.open_price - self.close_price) / pip_value
            self.pips_profit_loss = round(pips, 2)
        
        super().save(*args, **kwargs)
        
        # Update parent execution metrics
        if self.trade_status == 'closed':
            self.execution.update_performance_metrics()


class AlgorithmSignal(models.Model):
    """Track trading signals generated by algorithms"""
    SIGNAL_TYPES = [
        ('buy', 'Buy Signal'),
        ('sell', 'Sell Signal'),
        ('close', 'Close Signal'),
        ('modify', 'Modify Signal'),
    ]
    
    SIGNAL_STATUS = [
        ('generated', 'Generated'),
        ('executed', 'Executed'),
        ('failed', 'Failed to Execute'),
        ('ignored', 'Ignored'),
    ]
    
    execution = models.ForeignKey(AlgorithmExecution, on_delete=models.CASCADE, related_name='signals')
    
    # Signal details
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPES)
    symbol = models.CharField(max_length=20)
    signal_strength = models.DecimalField(max_digits=5, decimal_places=3, help_text="Signal confidence 0-1")
    
    # Recommended action
    recommended_volume = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    recommended_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    recommended_sl = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    recommended_tp = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    
    # Signal metadata
    signal_data = models.JSONField(default=dict, help_text="Technical analysis data")
    market_conditions = models.JSONField(default=dict, help_text="Market state when signal generated")
    
    # Execution tracking
    signal_status = models.CharField(max_length=20, choices=SIGNAL_STATUS, default='generated')
    trade_result = models.ForeignKey(TradeResult, on_delete=models.SET_NULL, null=True, blank=True)
    execution_message = models.TextField(null=True, blank=True)
    
    # Timing
    generated_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'algorithm_signals'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['execution', 'generated_at']),
            models.Index(fields=['symbol', 'generated_at']),
            models.Index(fields=['signal_status']),
        ]
    
    def __str__(self):
        return f"{self.signal_type.upper()} {self.symbol} - {self.signal_strength}"
