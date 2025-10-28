from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
    )

    COLLATERAL_CHOICES = (
        ('OFD', 'OFD'),
        ('NFT', 'NFT'),
        ('INVOICE', 'Invoice'),
        ('DIGITAL_ASSET', 'Digital Asset'),
    )

    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # in months
    purpose = models.TextField()
    repayment_schedule = models.JSONField()
    business_plan = models.FileField(upload_to='business_plans/', null=True, blank=True)
    collateral_type = models.CharField(max_length=20, choices=COLLATERAL_CHOICES, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    funded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan request of {self.amount} for {self.borrower}"

class Loan(models.Model):
    request = models.OneToOneField(LoanRequest, on_delete=models.CASCADE)
    lenders = models.ManyToManyField(User)
    is_funded = models.BooleanField(default=False)
    hcs_topic_id = models.CharField(max_length=255, blank=True, null=True)
    multi_sig_account_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Loan for request {self.request.id}"

class LoanTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('FUNDING', 'Funding'),
        ('REPAYMENT', 'Repayment'),
    )

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    hedera_transaction_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for loan {self.loan.id}"

    @property
    def explorer_link(self):
        if self.hedera_transaction_id:
            return f"https://hashscan.io/mainnet/transaction/{self.hedera_transaction_id}"
        return None
