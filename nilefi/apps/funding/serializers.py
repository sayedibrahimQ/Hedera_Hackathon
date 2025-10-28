from rest_framework import serializers
from .models import LoanRequest, Loan, LoanTransaction
from nilefi.apps.accounts.models import User

class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'kyc_verified')

class LoanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequest
        fields = ('id', 'amount', 'status', 'created_at')

class LoanRequestSerializer(serializers.ModelSerializer):
    borrower_details = BorrowerSerializer(source='borrower', read_only=True)
    loan_history = serializers.SerializerMethodField()
    repayment_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = LoanRequest
        fields = (
            'id', 'borrower', 'borrower_details', 'amount', 'duration', 'purpose', 'repayment_schedule',
            'business_plan', 'collateral_type', 'interest_rate', 'status', 'funded_amount',
            'repayment_breakdown', 'loan_history'
        )
        read_only_fields = ('borrower', 'interest_rate', 'repayment_breakdown', 'status', 'funded_amount')

    def get_loan_history(self, obj):
        history = LoanRequest.objects.filter(borrower=obj.borrower).exclude(id=obj.id)
        return LoanHistorySerializer(history, many=True).data

    def get_repayment_breakdown(self, obj):
        total_repayment = obj.amount * (1 + obj.interest_rate / 100)
        installment = total_repayment / obj.duration
        return {
            'total_repayment': total_repayment,
            'monthly_installment': installment
        }

    def create(self, validated_data):
        # Auto-calculate interest and repayment schedule
        validated_data['interest_rate'] = 5.0  # Simple interest for now
        amount = validated_data['amount']
        duration = validated_data['duration']
        interest_rate = validated_data['interest_rate']
        total_repayment = amount * (1 + interest_rate / 100)
        installment = total_repayment / duration
        repayment_schedule = {
            'installments': [
                {'installment': i + 1, 'amount': float(installment)} for i in range(duration)
            ]
        }
        validated_data['repayment_schedule'] = repayment_schedule
        validated_data['borrower'] = self.context['request'].user
        return super().create(validated_data)

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanTransactionSerializer(serializers.ModelSerializer):
    explorer_link = serializers.ReadOnlyField()

    class Meta:
        model = LoanTransaction
        fields = ('id', 'loan', 'user', 'transaction_type', 'amount', 'timestamp', 'hedera_transaction_id', 'explorer_link')


class FundLoanSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class RepayLoanSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
