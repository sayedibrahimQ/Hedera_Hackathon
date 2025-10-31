from rest_framework import serializers

class AccountSerializer(serializers.Serializer):
    private_key = serializers.CharField()
    public_key = serializers.CharField()
    account_id = serializers.CharField()

class WalletBalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField()
