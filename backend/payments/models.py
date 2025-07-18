from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans for the trading algorithms"""
    
    PLAN_TYPES = [
        ('basic', 'Basic Plan'),
        ('premium', 'Premium Plan'),
        ('pro', 'Professional Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    duration_days = models.IntegerField(default=30)  # 30 days = monthly
    max_algorithms = models.IntegerField(default=1)
    max_mt5_accounts = models.IntegerField(default=1)
    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - R{self.price}/{self.duration_days} days"


class Subscription(models.Model):
    """User subscriptions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    paystack_customer_code = models.CharField(max_length=100, blank=True)
    paystack_subscription_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and timezone.now() > self.end_date:
            return False
        return True
    
    @property
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if not self.end_date or not self.is_active:
            return 0
        remaining = self.end_date - timezone.now()
        return max(0, remaining.days)


class PaymentTransaction(models.Model):
    """Payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Payment'),
        ('renewal', 'Subscription Renewal'),
        ('upgrade', 'Plan Upgrade'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Paystack specific fields
    paystack_reference = models.CharField(max_length=100, unique=True)
    paystack_transaction_id = models.CharField(max_length=100, blank=True)
    paystack_authorization_code = models.CharField(max_length=100, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)  # card, bank_transfer, etc.
    gateway_response = models.JSONField(default=dict)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - R{self.amount} ({self.status})"


class PaystackWebhookLog(models.Model):
    """Log Paystack webhook events"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.CharField(max_length=100)
    reference = models.CharField(max_length=100, blank=True)
    data = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event} - {self.reference} ({'Processed' if self.processed else 'Pending'})"
