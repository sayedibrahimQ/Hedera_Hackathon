from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LoanRequest, Loan, LoanTransaction
from .serializers import (
    LoanRequestSerializer,
    LoanSerializer,
    LoanTransactionSerializer,
    FundLoanSerializer,
    RepayLoanSerializer
)
from blockchain.hcs import create_topic, submit_message
from blockchain.multi_sig import create_multi_sig_account, transfer_to_multi_sig, release_from_multi_sig

class LoanRequestListCreateView(generics.ListCreateAPIView):
    """View for creating and listing loan requests."""
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanRequestSerializer

    def get_queryset(self):
        return LoanRequest.objects.filter(borrower=self.request.user)

class LoanRequestDetailView(generics.RetrieveAPIView):
    """View for retrieving a single loan request."""
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanRequestSerializer
    queryset = LoanRequest.objects.all()

class BrowseLoanRequestsView(generics.ListAPIView):
    """View for lenders to browse and filter loan requests."""
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanRequestSerializer

    def get_queryset(self):
        queryset = LoanRequest.objects.filter(status='PENDING')
        sector = self.request.query_params.get('sector')
        if sector:
            queryset = queryset.filter(borrower__business_sector=sector)
        return queryset

class FundLoanView(views.APIView):
    """View for funding a loan."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        serializer = FundLoanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        try:
            loan_request = LoanRequest.objects.get(pk=pk, status='PENDING')
        except LoanRequest.DoesNotExist:
            return Response({"error": "Loan request not found or not available for funding."}, status=status.HTTP_404_NOT_FOUND)

        loan, created = Loan.objects.get_or_create(request=loan_request)
        lender = request.user

        if created:
            topic_id = create_topic()
            if not topic_id:
                return Response({"error": "Failed to create Hedera Consensus Service topic."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            loan.hcs_topic_id = topic_id

            borrower_public_key = loan_request.borrower.public_key
            lender_public_key = lender.public_key
            nilefi_public_key = "nilefi_public_key"
            multi_sig_account_id = create_multi_sig_account(borrower_public_key, lender_public_key, nilefi_public_key)
            if not multi_sig_account_id:
                return Response({"error": "Failed to create multi-signature account."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            loan.multi_sig_account_id = multi_sig_account_id

            loan_created_message = {
                "event": "LoanCreated",
                "loan_request_id": loan_request.id,
                "borrower": loan_request.borrower.username,
                "amount": str(loan_request.amount),
                "multi_sig_account_id": multi_sig_account_id,
            }
            submit_message(loan.hcs_topic_id, loan_created_message)

        hedera_transaction_id = transfer_to_multi_sig(lender.wallet_id, loan.multi_sig_account_id, amount)

        if not hedera_transaction_id:
            return Response({"error": "Failed to transfer funds to multi-sig account."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        loan.lenders.add(lender)
        loan_request.funded_amount += amount
        
        if loan_request.funded_amount >= loan_request.amount:
            loan_request.status = 'ACTIVE'
            loan.is_funded = True
        
        loan_request.save()
        loan.save()

        LoanTransaction.objects.create(
            loan=loan,
            user=lender,
            transaction_type='FUNDING',
            amount=amount,
            hedera_transaction_id=hedera_transaction_id
        )

        loan_funded_message = {
            "event": "LoanFunded",
            "lender": lender.username,
            "amount_funded": str(amount),
            "hedera_transaction_id": hedera_transaction_id,
        }
        submit_message(loan.hcs_topic_id, loan_funded_message)

        return Response({"status": "Loan funded successfully."}, status=status.HTTP_200_OK)

class ReleaseFundsView(views.APIView):
    """View to release funds from the multi-sig escrow to the borrower."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk, request__status='ACTIVE', is_funded=True)
        except Loan.DoesNotExist:
            return Response({"error": "Funded loan not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user != loan.request.borrower:
            return Response({"error": "Only the borrower can release the funds."}, status=status.HTTP_403_FORBIDDEN)

        partially_signed_tx = release_from_multi_sig(loan.multi_sig_account_id, loan.request.borrower.wallet_id, loan.request.amount)

        # In a real app, this partially signed transaction would be sent to the other parties to sign.
        # For now, we'll just simulate the event.
        
        funds_released_message = {
            "event": "FundsReleased",
            "loan_id": loan.id,
            "amount": str(loan.request.amount),
            "partially_signed_tx": partially_signed_tx
        }
        submit_message(loan.hcs_topic_id, funds_released_message)

        return Response({"status": "Funds release process initiated.", "partially_signed_transaction": partially_signed_tx}, status=status.HTTP_200_OK)

class RepayLoanView(views.APIView):
    """View for repaying a loan."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        serializer = RepayLoanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        try:
            loan = Loan.objects.get(pk=pk, request__borrower=request.user)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

        if not loan.hcs_topic_id or not loan.multi_sig_account_id:
            return Response({"error": "HCS topic or multi-sig account not found for this loan."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        borrower = request.user

        hedera_transaction_id = transfer_to_multi_sig(borrower.wallet_id, loan.multi_sig_account_id, amount)

        if not hedera_transaction_id:
            return Response({"error": "Failed to transfer funds to multi-sig account."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        LoanTransaction.objects.create(
            loan=loan,
            user=borrower,
            transaction_type='REPAYMENT',
            amount=amount,
            hedera_transaction_id=hedera_transaction_id
        )
        
        loan_repaid_message = {
            "event": "LoanRepaid",
            "borrower": borrower.username,
            "amount_repaid": str(amount),
            "hedera_transaction_id": hedera_transaction_id,
        }
        submit_message(loan.hcs_topic_id, loan_repaid_message)
        
        total_repaid = sum(t.amount for t in loan.loantransaction_set.filter(transaction_type='REPAYMENT'))
        if total_repaid >= loan.request.amount * (1 + loan.request.interest_rate/100):
            loan.request.status = 'COMPLETED'
            loan.request.save()
            loan_completed_message = {
                "event": "LoanCompleted",
                "loan_id": loan.id,
            }
            submit_message(loan.hcs_topic_id, loan_completed_message)

        return Response({"status": "Repayment successful."}, status=status.HTTP_200_OK)

class UserLoansView(generics.ListAPIView):
    """View to list loans for a user (both as borrower and lender)."""
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanSerializer

    def get_queryset(self):
        return Loan.objects.filter(request__borrower=self.request.user) | Loan.objects.filter(lenders=self.request.user)
