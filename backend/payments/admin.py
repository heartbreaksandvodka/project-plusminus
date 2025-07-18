from django.contrib import admin
from .models import SubscriptionPlan, Subscription, PaymentTransaction, PaystackWebhookLog


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'currency', 'duration_days', 'max_algorithms', 'is_active']
    list_filter = ['plan_type', 'is_active', 'currency']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew']
    list_filter = ['status', 'auto_renew', 'plan__plan_type']
    search_fields = ['user__email', 'plan__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'currency', 'status', 'paystack_reference', 'created_at']
    list_filter = ['status', 'transaction_type', 'currency']
    search_fields = ['user__email', 'paystack_reference', 'paystack_transaction_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'subscription']


@admin.register(PaystackWebhookLog)
class PaystackWebhookLogAdmin(admin.ModelAdmin):
    list_display = ['event', 'reference', 'processed', 'created_at']
    list_filter = ['event', 'processed']
    search_fields = ['reference', 'event']
    readonly_fields = ['id', 'created_at']
