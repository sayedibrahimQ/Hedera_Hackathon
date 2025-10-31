"""
Startup models for NileFi - managing SME profiles and onboarding.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class OnboardingStatus(models.TextChoices):
    """Onboarding status choices"""
    DRAFT = 'DRAFT', 'Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'


class Startup(models.Model):
    """
    Startup/SME profile model.
    Each startup is owned by a user and contains business information.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='startups'
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    
    # Financial Information (stored in profile_meta for flexibility)
    # Example: revenue, monthly_sales, business_age, etc.
    financial_data = models.JSONField(default=dict, blank=True)
    
    # Document storage (IPFS CIDs)
    # Structure: [{"cid": "Qm...", "name": "business_plan.pdf", "uploaded_at": "2025-..."}]
    ipfs_docs = models.JSONField(default=list, blank=True)
    
    # Onboarding & Approval
    onboarding_status = models.CharField(
        max_length=20,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.DRAFT
    )
    
    # Credit Score (calculated by AI module)
    credit_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="AI-calculated credit score (0-100)"
    )
    risk_level = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Risk assessment: Low, Medium, High"
    )
    score_explanation = models.JSONField(
        default=dict,
        blank=True,
        help_text="Feature importance and explanation for credit score"
    )
    
    # Blockchain tracking
    hcs_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Hedera Consensus Service message ID for onboarding"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'startups'
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'onboarding_status']),
            models.Index(fields=['sector', 'country']),
            models.Index(fields=['credit_score']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sector})"
    
    def approve(self):
        """Approve startup and set approved_at timestamp"""
        self.onboarding_status = OnboardingStatus.APPROVED
        self.approved_at = timezone.now()
        self.save(update_fields=['onboarding_status', 'approved_at'])
    
    def reject(self):
        """Reject startup application"""
        self.onboarding_status = OnboardingStatus.REJECTED
        self.save(update_fields=['onboarding_status'])
    
    @property
    def is_approved(self):
        """Check if startup is approved"""
        return self.onboarding_status == OnboardingStatus.APPROVED
    
    @property
    def document_count(self):
        """Count of uploaded documents"""
        return len(self.ipfs_docs)
