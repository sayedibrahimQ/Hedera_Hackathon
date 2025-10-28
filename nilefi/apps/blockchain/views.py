
from rest_framework import viewsets, status
from rest_framework.response import Response

from nilefi.apps.blockchain.serializers import (
    AccountSerializer,
    TokenizationSerializer,
    RentalAgreementSerializer,
)
from nilefi.apps.blockchain.transactions import (
    tokenize_real_estate_asset,
    setup_rental_agreement,
)
from nilefi.apps.blockchain.wallet_utils import create_account


class AccountViewSet(viewsets.ViewSet):
    """ViewSet for creating Hedera accounts."""

    def create(self, request):
        """Creates a new Hedera account."""
        private_key, public_key, account_id = create_account()
        serializer = AccountSerializer(
            {
                "private_key": private_key.toString(),
                "public_key": public_key.toString(),
                "account_id": account_id.toString(),
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TokenizationViewSet(viewsets.ViewSet):
    """ViewSet for tokenizing real estate assets."""

    def create(self, request):
        """Tokenizes a real estate asset."""
        serializer = TokenizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt = tokenize_real_estate_asset(**serializer.validated_data)

        return Response(
            {"status": "success", "receipt": receipt.toString()},
            status=status.HTTP_201_CREATED,
        )


class RentalAgreementViewSet(viewsets.ViewSet):
    """ViewSet for creating rental agreements."""

    def create(self, request):
        """Creates a rental agreement."""
        serializer = RentalAgreementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt = setup_rental_agreement(**serializer.validated_data)

        return Response(
            {"status": "success", "receipt": receipt.toString()},
            status=status.HTTP_201_CREATED,
        )
