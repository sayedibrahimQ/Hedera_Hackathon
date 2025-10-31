"""
Django admin configuration for investments app.
"""

from django.contrib import admin
from .models import Investment, AuditLog


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    """Admin interface for Investment model"""
    
    list_display = ['lender', 'funding_request', 'amount', 'status', 'deposited_at', 'created_at']
    list_filter = ['status', 'created_at', 'deposited_at']
    search_fields = ['lender__hedera_account_id', 'funding_request__title', 'deposit_tx_hash']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'deposited_at', 'completed_at']
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('funding_request', 'lender', 'amount', 'status')
        }),
        ('Blockchain Tracking', {
            'fields': ('deposit_tx_hash', 'hcs_deposit_message_id', 'escrow_contract_address', 'token_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deposited_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model"""
    
    list_display = ['event_type', 'user', 'hcs_message_id', 'transaction_hash', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['hcs_message_id', 'transaction_hash', 'user__hedera_account_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('event_type', 'user', 'payload')
        }),
        ('Blockchain References', {
            'fields': ('hcs_message_id', 'transaction_hash')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation of audit logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of audit logs"""
        return False
