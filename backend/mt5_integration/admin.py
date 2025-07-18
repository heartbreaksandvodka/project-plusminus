from django.contrib import admin
from .models import MT5Account, MT5TradingSession, AlgorithmExecution


@admin.register(MT5Account)
class MT5AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'broker_name', 'connection_status', 'account_type', 'last_connected']
    list_filter = ['connection_status', 'account_type', 'broker_name']
    search_fields = ['user__email', 'account_number', 'broker_name']
    readonly_fields = ['created_at', 'updated_at', 'last_connected']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'account_number', 'broker_name', 'server', 'account_type')
        }),
        ('Connection Status', {
            'fields': ('connection_status', 'last_connected', 'balance', 'equity', 'margin', 'currency')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(MT5TradingSession)
class MT5TradingSessionAdmin(admin.ModelAdmin):
    list_display = ['mt5_account', 'session_start', 'session_end', 'trades_executed', 'profit_loss']
    list_filter = ['session_start', 'mt5_account__broker_name']
    search_fields = ['mt5_account__user__email', 'mt5_account__account_number']
    readonly_fields = ['session_start']


@admin.register(AlgorithmExecution)
class AlgorithmExecutionAdmin(admin.ModelAdmin):
    list_display = ['algorithm_name', 'mt5_account', 'execution_status', 'started_at', 'profit_loss', 'trades_count']
    list_filter = ['execution_status', 'algorithm_name', 'started_at']
    search_fields = ['algorithm_name', 'mt5_account__user__email', 'mt5_account__account_number']
    readonly_fields = ['started_at']
