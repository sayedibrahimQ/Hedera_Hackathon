
from rest_framework import serializers


class AccountSerializer(serializers.Serializer):
    """Serializer for Hedera account creation."""

    private_key = serializers.CharField(read_only=True)
    public_key = serializers.CharField(read_only=True)
    account_id = serializers.CharField(read_only=True)


class TokenizationSerializer(serializers.Serializer):
    """Serializer for tokenizing a real estate asset."""

    property_id = serializers.CharField()
    owner_account_id = serializers.CharField()


class RentalAgreementSerializer(serializers.Serializer):
    """Serializer for creating a rental agreement."""

    property_id = serializers.CharField()
    tenant_account_id = serializers.CharField()
    rent_amount = serializers.IntegerField()
    duration = serializers.IntegerField()
