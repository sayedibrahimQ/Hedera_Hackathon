"""
Funding models for NileFi - managing funding requests and milestones.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from startups.models import Startup


class FundingStatus(models.TextChoices):
    """Funding request status choices"""
    DRAFT = 'DRAFT', 'Draft'
    OPEN = 'OPEN', 'Open for Funding'
    FUNDED = 'FUNDED', 'Fully Funded'
    ACTIVE = 'ACTIVE', 'Active (In Progress)'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class FundingRequest(models.Model):
    """
    Funding request/project created by a startup.
    Contains milestones for milestone-based funding release.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='funding_requests'
    )
    
    # Project Information
    title = models.CharField(max_length=300)
    description = models.TextField()
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total funding amount requested in HBAR"
    )
    
    # Funding tracking
    amount_raised = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount raised so far in HBAR"
    )
    
    status = models.CharField(
        max_length=20,
        choices=FundingStatus.choices,
        default=FundingStatus.DRAFT
    )
    
    # Blockchain tracking
    hedera_hcs_topic_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="HCS topic ID for this funding request"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    funded_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'funding_requests'
        verbose_name = 'Funding Request'
        verbose_name_plural = 'Funding Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['startup', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.startup.name}"
    
    @property
    def funding_progress_percentage(self):
        """Calculate funding progress percentage"""
        if self.total_amount == 0:
            return 0
        return float((self.amount_raised / self.total_amount) * 100)
    
    @property
    def is_fully_funded(self):
        """Check if funding goal is met"""
        return self.amount_raised >= self.total_amount
    
    @property
    def investor_count(self):
        """Count unique investors"""
        return self.investments.values('lender').distinct().count()
    
    def update_funding_status(self):
        """Update status based on funding progress"""
        if self.is_fully_funded and self.status == FundingStatus.OPEN:
            self.status = FundingStatus.FUNDED
            self.funded_at = timezone.now()
            self.save(update_fields=['status', 'funded_at'])


class MilestoneStatus(models.TextChoices):
    """Milestone status choices"""
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    VERIFIED = 'VERIFIED', 'Verified'
    RELEASED = 'RELEASED', 'Funds Released'
    REJECTED = 'REJECTED', 'Rejected'


class Milestone(models.Model):
    """
    Individual milestone within a funding request.
    Funds are released only when milestones are verified.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    funding_request = models.ForeignKey(
        FundingRequest,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    
    # Milestone Information
    title = models.CharField(max_length=300)
    description = models.TextField()
    order = models.IntegerField(default=1, help_text="Order/sequence of milestone")
    
    # Funding allocation
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount allocated to this milestone in HBAR"
    )
    percentage_of_request = models.IntegerField(
        help_text="Percentage of total funding request"
    )
    
    # Timeline
    due_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=MilestoneStatus.choices,
        default=MilestoneStatus.PENDING
    )
    
    # Proof of completion (IPFS CID)
    proof_ipfs_cid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="IPFS CID of proof documents"
    )
    
    # Blockchain tracking
    hcs_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="HCS message ID for milestone verification"
    )
    release_tx_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Hedera transaction hash for fund release"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'milestones'
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        ordering = ['funding_request', 'order']
        indexes = [
            models.Index(fields=['funding_request', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.funding_request.title}"
    
    def mark_complete(self, proof_cid):
        """Mark milestone as completed with proof"""
        self.status = MilestoneStatus.COMPLETED
        self.proof_ipfs_cid = proof_cid
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'proof_ipfs_cid', 'completed_at'])
    
    def verify(self, hcs_message_id):
        """Verify milestone completion"""
        self.status = MilestoneStatus.VERIFIED
        self.hcs_message_id = hcs_message_id
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'hcs_message_id', 'verified_at'])
    
    def release_funds(self, tx_hash):
        """Release funds for this milestone"""
        self.status = MilestoneStatus.RELEASED
        self.release_tx_hash = tx_hash
        self.released_at = timezone.now()
        self.save(update_fields=['status', 'release_tx_hash', 'released_at'])
