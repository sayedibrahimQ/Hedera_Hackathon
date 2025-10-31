"""
Investment models for NileFi - tracking lender investments and deposits.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from funding.models import FundingRequest


class InvestmentStatus(models.TextChoices):
    """Investment status choices"""
    PENDING = 'PENDING', 'Pending Deposit'
    DEPOSITED = 'DEPOSITED', 'Deposited to Escrow'
    ACTIVE = 'ACTIVE', 'Active'
    COMPLETED = 'COMPLETED', 'Completed'
    REFUNDED = 'REFUNDED', 'Refunded'


class Investment(models.Model):
    """
    Investment/deposit from a lender to a funding request.
    Tracks the deposit transaction and escrow details.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    funding_request = models.ForeignKey(
        FundingRequest,
        on_delete=models.CASCADE,
        related_name='investments'
    )
    
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investments',
        limit_choices_to={'role': 'LENDER'}
    )
    
    # Investment amount
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Investment amount in HBAR"
    )
    
    status = models.CharField(
        max_length=20,
        choices=InvestmentStatus.choices,
        default=InvestmentStatus.PENDING
    )
    
    # Blockchain tracking
    deposit_tx_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Hedera transaction hash for deposit"
    )
    
    escrow_contract_address = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Smart contract address (if using contract escrow)"
    )
    
    # HTS token tracking (for future OFD integration)
    token_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Hedera Token ID (for OFD or tokenized investments)"
    )
    
    # HCS tracking
    hcs_deposit_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="HCS message ID for deposit event"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deposited_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'investments'
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['funding_request', 'status']),
            models.Index(fields=['lender', 'status']),
            models.Index(fields=['deposit_tx_hash']),
        ]
    
    def __str__(self):
        return f"{self.lender.hedera_account_id} -> {self.funding_request.title} ({self.amount} HBAR)"
    
    def confirm_deposit(self, tx_hash, hcs_message_id):
        """Confirm deposit transaction"""
        self.status = InvestmentStatus.DEPOSITED
        self.deposit_tx_hash = tx_hash
        self.hcs_deposit_message_id = hcs_message_id
        self.deposited_at = timezone.now()
        self.save(update_fields=['status', 'deposit_tx_hash', 'hcs_deposit_message_id', 'deposited_at'])
        
        # Update funding request's raised amount
        self.funding_request.amount_raised += self.amount
        self.funding_request.save(update_fields=['amount_raised'])
        self.funding_request.update_funding_status()
    
    def complete(self):
        """Mark investment as completed"""
        self.status = InvestmentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def refund(self):
        """Mark investment as refunded"""
        self.status = InvestmentStatus.REFUNDED
        self.save(update_fields=['status'])


class AuditLog(models.Model):
    """
    Audit log for all blockchain-related events.
    Provides a comprehensive record of all system actions.
    """
    
    EVENT_TYPES = [
        ('CREATE_REQUEST', 'Create Funding Request'),
        ('DEPOSIT', 'Investment Deposit'),
        ('MILESTONE_COMPLETE', 'Milestone Completed'),
        ('VERIFY_MILESTONE', 'Milestone Verified'),
        ('RELEASE_FUNDS', 'Funds Released'),
        ('REFUND', 'Refund Processed'),
        ('STARTUP_APPROVED', 'Startup Approved'),
        ('SCORE_CALCULATED', 'Credit Score Calculated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    # Event details (flexible JSON structure)
    payload = models.JSONField(default=dict)
    
    # Blockchain reference
    hcs_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="HCS message ID for this event"
    )
    
    transaction_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Hedera transaction hash (if applicable)"
    )
    
    # User tracking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['hcs_message_id']),
            models.Index(fields=['transaction_hash']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
