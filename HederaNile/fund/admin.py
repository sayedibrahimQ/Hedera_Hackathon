"""
Django admin configuration for funding app.
"""

from django.contrib import admin
from .models import FundingRequest, Milestone


class MilestoneInline(admin.TabularInline):
    """Inline admin for milestones"""
    model = Milestone
    extra = 0
    fields = ['order', 'title', 'target_amount', 'percentage_of_request', 'status', 'due_date']
    readonly_fields = []


@admin.register(FundingRequest)
class FundingRequestAdmin(admin.ModelAdmin):
    """Admin interface for FundingRequest model"""
    
    list_display = ['title', 'startup', 'total_amount', 'amount_raised', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'startup__name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'funded_at', 'completed_at', 'funding_progress_percentage', 'investor_count']
    inlines = [MilestoneInline]
    
    fieldsets = (
        ('Project Details', {
            'fields': ('startup', 'title', 'description')
        }),
        ('Funding', {
            'fields': ('total_amount', 'amount_raised', 'funding_progress_percentage', 'investor_count', 'status')
        }),
        ('Blockchain', {
            'fields': ('hedera_hcs_topic_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'funded_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """Admin interface for Milestone model"""
    
    list_display = ['title', 'funding_request', 'order', 'target_amount', 'status', 'due_date']
    list_filter = ['status', 'due_date']
    search_fields = ['title', 'funding_request__title']
    ordering = ['funding_request', 'order']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'verified_at', 'released_at']
    
    fieldsets = (
        ('Milestone Details', {
            'fields': ('funding_request', 'order', 'title', 'description', 'due_date')
        }),
        ('Funding Allocation', {
            'fields': ('target_amount', 'percentage_of_request')
        }),
        ('Status & Proof', {
            'fields': ('status', 'proof_ipfs_cid')
        }),
        ('Blockchain Tracking', {
            'fields': ('hcs_message_id', 'release_tx_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'verified_at', 'released_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_milestones']
    
    def verify_milestones(self, request, queryset):
        """Bulk verify milestones"""
        count = queryset.filter(status='COMPLETED').update(status='VERIFIED')
        self.message_user(request, f"{count} milestones verified.")
    verify_milestones.short_description = "Verify completed milestones"
