from django.db import models
from django.conf import settings

class FundingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    amount_requested = models.DecimalField(max_digits=18, decimal_places=2)
    milestones = models.JSONField()  # Stores milestones as JSON
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='funding_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Investment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investments')
    funding_request = models.ForeignKey(FundingRequest, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)  # Hedera transaction hash
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Investment by {self.investor.username} in {self.funding_request.title}"

class Milestone(models.Model):
    funding_request = models.ForeignKey(FundingRequest, on_delete=models.CASCADE, related_name='project_milestones')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    proof_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ('funding_request', 'order')

    def __str__(self):
        return f"Milestone {self.order} for {self.funding_request.title}"
