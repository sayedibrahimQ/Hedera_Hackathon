"""
Django REST Framework serializers for startups app.
"""
from rest_framework import serializers
from .models import Startup
from accounts.serializers import UserPublicSerializer
import json


class StartupCreateSerializer(serializers.ModelSerializer):
    """Serializer for startup profile creation."""
    
    class Meta:
        model = Startup
        fields = ['name', 'sector', 'country', 'description', 'revenue', 
                 'monthly_sales', 'business_age', 'ipfs_docs']
        extra_kwargs = {
            'name': {'required': True},
            'sector': {'required': True},
            'country': {'required': True},
            'description': {'required': True},
            'revenue': {'required': True},
            'monthly_sales': {'required': True},
            'business_age': {'required': True}
        }
    
    def validate_revenue(self, value):
        """Validate revenue is positive."""
        if value < 0:
            raise serializers.ValidationError("Revenue cannot be negative")
        return value
    
    def validate_monthly_sales(self, value):
        """Validate monthly sales is positive."""
        if value < 0:
            raise serializers.ValidationError("Monthly sales cannot be negative")
        return value
    
    def validate_business_age(self, value):
        """Validate business age is reasonable."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Business age must be between 0 and 100 years")
        return value
    
    def validate_ipfs_docs(self, value):
        """Validate IPFS docs structure."""
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("ipfs_docs must be a list")
            for doc in value:
                if not isinstance(doc, dict) or 'cid' not in doc or 'filename' not in doc:
                    raise serializers.ValidationError(
                        "Each document must have 'cid' and 'filename' fields"
                    )
        return value


class StartupUpdateSerializer(serializers.ModelSerializer):
    """Serializer for startup profile updates."""
    
    class Meta:
        model = Startup
        fields = ['name', 'sector', 'country', 'description', 'revenue', 
                 'monthly_sales', 'business_age', 'ipfs_docs']
    
    def validate_revenue(self, value):
        """Validate revenue is positive."""
        if value < 0:
            raise serializers.ValidationError("Revenue cannot be negative")
        return value
    
    def validate_monthly_sales(self, value):
        """Validate monthly sales is positive."""
        if value < 0:
            raise serializers.ValidationError("Monthly sales cannot be negative")
        return value


class StartupDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed startup information."""
    owner = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Startup
        fields = ['id', 'owner', 'name', 'sector', 'country', 'description', 
                 'revenue', 'monthly_sales', 'business_age', 'ipfs_docs', 
                 'credit_score', 'onboarding_status', 'hcs_create_message_id',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'credit_score', 'onboarding_status', 
                           'hcs_create_message_id', 'created_at', 'updated_at']


class StartupListSerializer(serializers.ModelSerializer):
    """Serializer for startup list view (marketplace)."""
    owner = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Startup
        fields = ['id', 'owner', 'name', 'sector', 'country', 'description', 
                 'revenue', 'credit_score', 'onboarding_status', 'created_at']


class StartupPublicSerializer(serializers.ModelSerializer):
    """Serializer for public startup information (used in funding displays)."""
    
    class Meta:
        model = Startup
        fields = ['id', 'name', 'sector', 'country', 'description', 'credit_score']


class StartupOnboardingSerializer(serializers.ModelSerializer):
    """Serializer for admin onboarding status updates."""
    
    class Meta:
        model = Startup
        fields = ['onboarding_status']
        extra_kwargs = {
            'onboarding_status': {'required': True}
        }


class StartupScoringSerializer(serializers.Serializer):
    """Serializer for AI credit scoring results."""
    startup_id = serializers.UUIDField()
    score = serializers.IntegerField(min_value=0, max_value=100)
    risk_bucket = serializers.CharField()
    feature_importance = serializers.DictField()
    explanation = serializers.CharField()
    scoring_date = serializers.DateTimeField()


class StartupStatsSerializer(serializers.Serializer):
    """Serializer for startup statistics (admin dashboard)."""
    total_startups = serializers.IntegerField()
    pending_approval = serializers.IntegerField()
    approved_startups = serializers.IntegerField()
    rejected_startups = serializers.IntegerField()
    avg_credit_score = serializers.FloatField()
    top_sectors = serializers.ListField(child=serializers.DictField())
    new_startups_week = serializers.IntegerField()


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload to IPFS."""
    file = serializers.FileField()
    document_type = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False)
    
    def validate_file(self, value):
        """Validate file size and type."""
        # Max file size: 10MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Allowed file types
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF, DOC, DOCX, JPG, and PNG files are allowed"
            )
        
        return value