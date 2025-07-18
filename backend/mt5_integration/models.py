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
    
    # Error tracking
    error_message = models.TextField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'algorithm_executions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.algorithm_name} on {self.mt5_account.account_number}"
