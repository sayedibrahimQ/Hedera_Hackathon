from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import RegisterSerializer, UserSerializer
from blockchain.wallet_utils import create_account


class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveAPIView):
    """View for retrieving user profile."""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SetWalletView(views.APIView):
    """View for setting or creating a user's wallet."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Create a new Hedera account and link it to the user."""
        user = request.user
        if user.wallet_id:
            return Response(
                {"error": "User already has a wallet."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        private_key, public_key, account_id = create_account()
        user.wallet_id = account_id.toString()
        user.save()

        return Response({
            "wallet_id": user.wallet_id,
            "private_key": private_key.toString(),
            "public_key": public_key.toString()
        }, status=status.HTTP_201_CREATED)


class KYCUploadView(views.APIView):
    """View for uploading KYC documents."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Handles KYC document upload.
        In a real application, you would save the file and trigger a verification process.
        For now, we'll just mark the user as kyc_verified.
        """
        user = request.user
        # In a real app: handle file upload, save it, and queue for verification
        # For example: serializer = KYCDocumentSerializer(data=request.data)
        # if serializer.is_valid(): ...
        user.kyc_verified = True
        user.save()
        return Response({"status": "KYC verification pending"}, status=status.HTTP_200_OK)
