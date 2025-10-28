from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('MINT', 'Mint'),
        ('TRANSFER', 'Transfer'),
        ('BURN', 'Burn'),
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    sender = models.CharField(max_length=255, null=True, blank=True)
    receiver = models.CharField(max_length=255, null=True, blank=True)
    amount = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} from {self.sender} to {self.receiver}"
