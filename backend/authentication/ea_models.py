"""
EA Authentication Token Model
Extends existing authentication system for EA-specific token management
"""

from django.db import models
from django.contrib.auth import get_user_model
import secrets
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class EAAuthToken(models.Model):
    """
    Authentication tokens specifically for EA (Expert Advisor) connections
    These tokens are separate from user JWT tokens and are scoped for EA operations
    """
    
    # Token ownership and identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ea_tokens')
    algorithm_id = models.CharField(max_length=100, help_text="Unique identifier for the EA/algorithm")
    name = models.CharField(max_length=200, help_text="Human-readable name for the EA")
    
    # Token data
    token = models.CharField(max_length=128, unique=True, help_text="The actual token string")
    token_hash = models.CharField(max_length=64, help_text="SHA256 hash of the token for security")
    
    # Token metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text="Token expiration time")
    is_active = models.BooleanField(default=True)
    
    # EA-specific permissions and settings
    permissions = models.JSONField(default=dict, help_text="Specific permissions for this EA token")
    settings = models.JSONField(default=dict, help_text="EA-specific settings and configuration")
    
    # Usage tracking
    connection_count = models.IntegerField(default=0, help_text="Number of times this token has been used to connect")
    last_ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "EA Authentication Token"
        verbose_name_plural = "EA Authentication Tokens"
        unique_together = ['user', 'algorithm_id']  # One token per user per algorithm
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['algorithm_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.token:
            # Generate a secure token
            self.token = self.generate_token()
            self.token_hash = self.hash_token(self.token)
        
        if not self.expires_at:
            # Default expiration: 30 days
            self.expires_at = timezone.now() + timedelta(days=30)
        
        # Set default permissions if none provided
        if not self.permissions:
            self.permissions = {
                'websocket_connect': True,
                'send_trades': True,
                'send_signals': True,
                'send_status': True,
                'receive_commands': True
            }
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(64)  # 86 characters, URL-safe
    
    @staticmethod
    def hash_token(token):
        """Create SHA256 hash of token for secure storage lookup"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return (
            self.is_active and 
            timezone.now() < self.expires_at
        )
    
    def extend_expiration(self, days=30):
        """Extend token expiration by specified days"""
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=['expires_at'])
    
    def mark_used(self, ip_address=None):
        """Mark token as used and update usage statistics"""
        self.last_used = timezone.now()
        self.connection_count += 1
        if ip_address and ip_address != 'unknown':
            # Validate IP address before saving
            try:
                import ipaddress
                ipaddress.ip_address(ip_address)
                self.last_ip_address = ip_address
            except ValueError:
                # Invalid IP address, use localhost as fallback
                self.last_ip_address = '127.0.0.1'
        elif not self.last_ip_address:
            # If no valid IP provided and no previous IP, use localhost
            self.last_ip_address = '127.0.0.1'
        self.save(update_fields=['last_used', 'connection_count', 'last_ip_address'])
    
    def revoke(self):
        """Revoke the token by marking it inactive"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def update_permissions(self, new_permissions):
        """Update token permissions"""
        self.permissions.update(new_permissions)
        self.save(update_fields=['permissions'])
    
    def has_permission(self, permission):
        """Check if token has specific permission"""
        return self.permissions.get(permission, False)
    
    @classmethod
    def validate_token(cls, token_string):
        """
        Validate a token string and return the token object if valid
        Returns None if token is invalid or expired
        """
        try:
            token_hash = cls.hash_token(token_string)
            token = cls.objects.get(token_hash=token_hash, is_active=True)
            
            if token.is_valid():
                return token
            else:
                # Token expired
                token.revoke()
                return None
                
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def create_for_user(cls, user, algorithm_id, name, **kwargs):
        """
        Create a new EA token for a user and algorithm
        Replaces existing token if one exists for the same user/algorithm
        """
        # Revoke existing token if it exists
        existing_tokens = cls.objects.filter(
            user=user, 
            algorithm_id=algorithm_id,
            is_active=True
        )
        for token in existing_tokens:
            token.revoke()
        
        # Create new token
        return cls.objects.create(
            user=user,
            algorithm_id=algorithm_id,
            name=name,
            **kwargs
        )
    
    def __str__(self):
        return f"EA Token: {self.name} ({self.algorithm_id}) for {self.user.email}"


class EAConnectionLog(models.Model):
    """
    Log of EA connections for monitoring and debugging
    """
    ea_token = models.ForeignKey(EAAuthToken, on_delete=models.CASCADE, related_name='connection_logs')
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    connection_duration = models.DurationField(null=True, blank=True)
    disconnect_reason = models.CharField(max_length=100, blank=True)
    
    # Connection statistics
    messages_sent = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    trades_reported = models.IntegerField(default=0)
    errors_encountered = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "EA Connection Log"
        verbose_name_plural = "EA Connection Logs"
        indexes = [
            models.Index(fields=['ea_token', 'connected_at']),
            models.Index(fields=['connected_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Validate IP address before saving
        if self.ip_address and self.ip_address != 'unknown':
            try:
                import ipaddress
                ipaddress.ip_address(self.ip_address)
            except ValueError:
                # Invalid IP address, use localhost as fallback
                self.ip_address = '127.0.0.1'
        elif not self.ip_address or self.ip_address == 'unknown':
            # If no valid IP provided, use localhost
            self.ip_address = '127.0.0.1'
        
        super().save(*args, **kwargs)
    
    def mark_disconnected(self, reason=""):
        """Mark connection as disconnected and calculate duration"""
        self.disconnected_at = timezone.now()
        self.disconnect_reason = reason
        if self.connected_at:
            self.connection_duration = self.disconnected_at - self.connected_at
        self.save(update_fields=['disconnected_at', 'disconnect_reason', 'connection_duration'])
    
    def increment_counter(self, counter_name):
        """Increment a specific counter (messages_sent, messages_received, etc.)"""
        if hasattr(self, counter_name):
            current_value = getattr(self, counter_name)
            setattr(self, counter_name, current_value + 1)
            self.save(update_fields=[counter_name])
    
    def __str__(self):
        status = "Active" if not self.disconnected_at else "Disconnected"
        return f"EA Connection: {self.ea_token.name} - {status} ({self.connected_at})"
