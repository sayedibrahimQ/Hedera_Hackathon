from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nilefi.apps.blockchain.serializers import (
    WalletBalanceSerializer
)
from nilefi.apps.blockchain.wallet_utils import get_account_balance


class OFDWalletView(views.APIView):
    """View for OFD wallet operations."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Get the user's OFD token balance."""
        user = request.user
        if not user.wallet_id:
            return Response({"error": "User does not have a wallet."}, status=status.HTTP_400_BAD_REQUEST)
        
        balance = get_account_balance(user.wallet_id)
        serializer = WalletBalanceSerializer(data={'balance': balance})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
