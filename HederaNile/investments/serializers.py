"""
Django REST Framework serializers for investments app.
"""
from rest_framework import serializers
from .models import Investment, AuditLog
from funding.serializers import FundingRequestListSerializer
from accounts.serializers import UserPublicSerializer
from decimal import Decimal


class InvestmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating investments."""
    
    class Meta:
        model = Investment
        fields = ['funding_request', 'amount']
        extra_kwargs = {
            'funding_request': {'required': True},
            'amount': {'required': True}
        }
    
    def validate_amount(self, value):
        """Validate investment amount."""
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be positive")
        
        # Minimum investment: $100
        if value < Decimal('100.00'):
            raise serializers.ValidationError("Minimum investment amount is $100")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        funding_request = attrs['funding_request']
        amount = attrs['amount']
        
        # Check if funding request is open for investments
        if funding_request.status not in ['OPEN', 'FUNDED']:
            raise serializers.ValidationError(
                "This funding request is not open for investments"
            )
        
        # Check if investment would exceed funding goal
        if funding_request.current_amount + amount > funding_request.total_amount:
            available = funding_request.total_amount - funding_request.current_amount
            raise serializers.ValidationError(
                f"Investment amount exceeds available funding. Available: ${available}"
            )
        
        return attrs


class InvestmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed investment view."""
    funding_request = FundingRequestListSerializer(read_only=True)
    lender = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Investment
        fields = ['id', 'funding_request', 'lender', 'amount', 'status',
                 'deposit_tx_hash', 'hcs_deposit_message_id', 'escrow_contract_address',
                 'token_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'deposit_tx_hash', 'hcs_deposit_message_id',
                           'escrow_contract_address', 'token_id', 'created_at', 'updated_at']


class InvestmentListSerializer(serializers.ModelSerializer):
    """Serializer for investment list view."""
    funding_request = serializers.SerializerMethodField()
    lender = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Investment
        fields = ['id', 'funding_request', 'lender', 'amount', 'status', 'created_at']
    
    def get_funding_request(self, obj):
        """Get basic funding request info."""
        return {
            'id': obj.funding_request.id,
            'title': obj.funding_request.title,
            'startup_name': obj.funding_request.startup.name,
            'total_amount': obj.funding_request.total_amount
        }


class InvestmentStatusSerializer(serializers.ModelSerializer):
    """Serializer for investment status updates."""
    
    class Meta:
        model = Investment
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }


class InvestmentTransactionSerializer(serializers.Serializer):
    """Serializer for blockchain transaction details."""
    investment_id = serializers.UUIDField()
    transaction_hash = serializers.CharField(max_length=200)
    transaction_type = serializers.ChoiceField(choices=['DEPOSIT', 'RELEASE', 'REFUND'])
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    hedera_account_from = serializers.CharField(max_length=50)
    hedera_account_to = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries."""
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'event_type', 'user', 'payload', 'hcs_message_id',
                 'transaction_hash', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuditLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating audit log entries."""
    
    class Meta:
        model = AuditLog
        fields = ['event_type', 'payload', 'hcs_message_id', 'transaction_hash']
        extra_kwargs = {
            'event_type': {'required': True},
            'payload': {'required': True}
        }
    
    def validate_payload(self, value):
        """Validate payload is valid JSON."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload must be a valid JSON object")
        return value


class InvestmentStatsSerializer(serializers.Serializer):
    """Serializer for investment statistics."""
    total_investments = serializers.IntegerField()
    pending_investments = serializers.IntegerField()
    deposited_investments = serializers.IntegerField()
    completed_investments = serializers.IntegerField()
    refunded_investments = serializers.IntegerField()
    total_amount_invested = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_amount_released = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    top_lenders = serializers.ListField(child=serializers.DictField())
    investment_trend = serializers.ListField(child=serializers.DictField())


class LenderDashboardSerializer(serializers.Serializer):
    """Serializer for lender dashboard data."""
    total_invested = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_investments = serializers.IntegerField()
    completed_investments = serializers.IntegerField()
    total_returns = serializers.DecimalField(max_digits=15, decimal_places=2)
    portfolio_performance = serializers.FloatField()
    recent_investments = InvestmentListSerializer(many=True)
    investment_distribution = serializers.ListField(child=serializers.DictField())


class StartupDashboardSerializer(serializers.Serializer):
    """Serializer for startup dashboard data."""
    total_funding_requests = serializers.IntegerField()
    total_amount_requested = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_amount_raised = serializers.DecimalField(max_digits=15, decimal_places=2)
    funding_success_rate = serializers.FloatField()
    active_milestones = serializers.IntegerField()
    completed_milestones = serializers.IntegerField()
    recent_investments = InvestmentListSerializer(many=True)
    milestone_progress = serializers.ListField(child=serializers.DictField())


class AdminDashboardSerializer(serializers.Serializer):
    """Serializer for admin dashboard data."""
    platform_stats = serializers.DictField()
    user_stats = serializers.DictField()
    funding_stats = serializers.DictField()
    investment_stats = serializers.DictField()
    recent_activities = AuditLogSerializer(many=True)
    pending_approvals = serializers.DictField()
    system_health = serializers.DictField()


class BlockchainStatusSerializer(serializers.Serializer):
    """Serializer for blockchain integration status."""
    hedera_network_status = serializers.CharField()
    mirror_node_status = serializers.CharField()
    escrow_account_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    hcs_topic_count = serializers.IntegerField()
    recent_transactions = serializers.ListField(child=serializers.DictField())
    ipfs_status = serializers.CharField()
    pinata_usage = serializers.DictField()


class RefundRequestSerializer(serializers.Serializer):
    """Serializer for investment refund requests."""
    investment_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=1000)
    refund_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    def validate_refund_amount(self, value):
        """Validate refund amount."""
        if value and value <= 0:
            raise serializers.ValidationError("Refund amount must be positive")
        return value


class EscrowReleaseSerializer(serializers.Serializer):
    """Serializer for escrow fund release."""
    milestone_id = serializers.UUIDField()
    release_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    recipient_account = serializers.CharField(max_length=50)
    admin_notes = serializers.CharField(max_length=1000, required=False)
    
    def validate_release_amount(self, value):
        """Validate release amount."""
        if value <= 0:
            raise serializers.ValidationError("Release amount must be positive")
        return value
    
    def validate_recipient_account(self, value):
        """Validate Hedera account ID format."""
        if not value.startswith('0.0.'):
            raise serializers.ValidationError("Invalid Hedera account ID format")
        return value


class WalletConnectSerializer(serializers.Serializer):
    """Serializer for wallet connection verification."""
    wallet_type = serializers.ChoiceField(choices=['HashPack', 'Blade'])
    account_id = serializers.CharField(max_length=50)
    public_key = serializers.CharField(max_length=200)
    network = serializers.ChoiceField(choices=['testnet', 'mainnet'])
    
    def validate_account_id(self, value):
        """Validate Hedera account ID format."""
        if not value.startswith('0.0.'):
            raise serializers.ValidationError("Invalid Hedera account ID format")
        return value