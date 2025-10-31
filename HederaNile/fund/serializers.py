"""
Django REST Framework serializers for funding app.
"""
from rest_framework import serializers
from .models import FundingRequest, Milestone
from startups.serializers import StartupPublicSerializer
from decimal import Decimal
from datetime import date, timedelta


class MilestoneCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating milestones within funding request."""
    
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'target_amount', 'percentage', 'due_date']
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
            'target_amount': {'required': True},
            'percentage': {'required': True},
            'due_date': {'required': True}
        }
    
    def validate_target_amount(self, value):
        """Validate target amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be positive")
        return value
    
    def validate_percentage(self, value):
        """Validate percentage is between 0 and 100."""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("Percentage must be between 1 and 100")
        return value
    
    def validate_due_date(self, value):
        """Validate due date is in the future."""
        if value <= date.today():
            raise serializers.ValidationError("Due date must be in the future")
        return value


class MilestoneDetailSerializer(serializers.ModelSerializer):
    """Serializer for milestone details."""
    
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'description', 'target_amount', 'percentage',
                 'due_date', 'status', 'proof_ipfs_cid', 'hcs_verify_message_id',
                 'release_tx_hash', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'hcs_verify_message_id', 
                           'release_tx_hash', 'created_at', 'updated_at']


class MilestoneUpdateSerializer(serializers.ModelSerializer):
    """Serializer for milestone updates (startup can update before funding)."""
    
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'target_amount', 'percentage', 'due_date']
    
    def validate_target_amount(self, value):
        """Validate target amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be positive")
        return value


class MilestoneProofSerializer(serializers.Serializer):
    """Serializer for milestone proof submission."""
    milestone_id = serializers.UUIDField()
    proof_file = serializers.FileField()
    description = serializers.CharField(max_length=1000)
    
    def validate_proof_file(self, value):
        """Validate proof file."""
        # Max file size: 20MB
        max_size = 20 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Proof file cannot exceed 20MB")
        
        # Allowed file types for proof
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'video/mp4',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF, DOC, DOCX, JPG, PNG, and MP4 files are allowed for proof"
            )
        
        return value


class MilestoneVerificationSerializer(serializers.Serializer):
    """Serializer for admin milestone verification."""
    milestone_id = serializers.UUIDField()
    verification_status = serializers.ChoiceField(choices=['VERIFIED', 'REJECTED'])
    admin_notes = serializers.CharField(max_length=1000, required=False)


class FundingRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating funding requests."""
    milestones = MilestoneCreateSerializer(many=True, required=True)
    
    class Meta:
        model = FundingRequest
        fields = ['title', 'description', 'total_amount', 'milestones']
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
            'total_amount': {'required': True}
        }
    
    def validate_total_amount(self, value):
        """Validate total amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be positive")
        return value
    
    def validate_milestones(self, value):
        """Validate milestones structure and totals."""
        if not value or len(value) < 1:
            raise serializers.ValidationError("At least one milestone is required")
        
        total_percentage = sum(milestone['percentage'] for milestone in value)
        if abs(total_percentage - 100) > 0.01:  # Allow small floating point errors
            raise serializers.ValidationError("Milestone percentages must sum to 100%")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        total_amount = attrs['total_amount']
        milestones = attrs['milestones']
        
        # Calculate milestone amounts and verify they sum correctly
        calculated_total = Decimal('0')
        for milestone in milestones:
            milestone_amount = total_amount * (milestone['percentage'] / 100)
            calculated_total += milestone_amount
        
        # Allow small rounding differences
        if abs(calculated_total - total_amount) > Decimal('0.01'):
            raise serializers.ValidationError(
                "Milestone amounts don't sum to total amount correctly"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create funding request with milestones."""
        milestones_data = validated_data.pop('milestones')
        funding_request = FundingRequest.objects.create(**validated_data)
        
        for milestone_data in milestones_data:
            # Calculate actual target amount based on percentage
            milestone_data['target_amount'] = funding_request.total_amount * (
                milestone_data['percentage'] / 100
            )
            milestone_data['funding_request'] = funding_request
            Milestone.objects.create(**milestone_data)
        
        return funding_request


class FundingRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed funding request view."""
    startup = StartupPublicSerializer(read_only=True)
    milestones = MilestoneDetailSerializer(many=True, read_only=True)
    funding_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = FundingRequest
        fields = ['id', 'startup', 'title', 'description', 'total_amount', 
                 'current_amount', 'status', 'funding_percentage', 'hcs_topic_id',
                 'milestones', 'created_at', 'updated_at']
        read_only_fields = ['id', 'current_amount', 'status', 'hcs_topic_id',
                           'created_at', 'updated_at']
    
    def get_funding_percentage(self, obj):
        """Calculate funding percentage."""
        if obj.total_amount > 0:
            return round((obj.current_amount / obj.total_amount) * 100, 2)
        return 0


class FundingRequestListSerializer(serializers.ModelSerializer):
    """Serializer for funding request list view (marketplace)."""
    startup = StartupPublicSerializer(read_only=True)
    funding_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = FundingRequest
        fields = ['id', 'startup', 'title', 'description', 'total_amount', 
                 'current_amount', 'status', 'funding_percentage', 'created_at']
    
    def get_funding_percentage(self, obj):
        """Calculate funding percentage."""
        if obj.total_amount > 0:
            return round((obj.current_amount / obj.total_amount) * 100, 2)
        return 0


class FundingRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for funding request updates (before funding starts)."""
    
    class Meta:
        model = FundingRequest
        fields = ['title', 'description', 'total_amount']
    
    def validate_total_amount(self, value):
        """Validate total amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be positive")
        return value


class FundingRequestStatusSerializer(serializers.ModelSerializer):
    """Serializer for funding request status updates (admin)."""
    
    class Meta:
        model = FundingRequest
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }


class FundingStatsSerializer(serializers.Serializer):
    """Serializer for funding statistics (dashboard)."""
    total_requests = serializers.IntegerField()
    active_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    total_amount_requested = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_amount_funded = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_funding_percentage = serializers.FloatField()
    top_sectors = serializers.ListField(child=serializers.DictField())
    new_requests_week = serializers.IntegerField()


class MarketplaceFilterSerializer(serializers.Serializer):
    """Serializer for marketplace filtering and search."""
    search = serializers.CharField(max_length=100, required=False)
    sector = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    status = serializers.ChoiceField(choices=FundingRequest.STATUS_CHOICES, required=False)
    min_credit_score = serializers.IntegerField(min_value=0, max_value=100, required=False)
    ordering = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'total_amount', '-total_amount', 
                'credit_score', '-credit_score'],
        required=False,
        default='-created_at'
    )