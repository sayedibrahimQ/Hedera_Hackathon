from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET -> current user profile
    PATCH -> update certain fields (display_name, wallet_id)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        # allow updating display_name and wallet_id via patch
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# A small convenience endpoint to set wallet_id for the authenticated user
class SetWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet_id = request.data.get('wallet_id')
        if not wallet_id:
            return Response({"detail": "wallet_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.wallet_id = wallet_id
        user.save(update_fields=['wallet_id'])
        return Response({"wallet_id": user.wallet_id}, status=status.HTTP_200_OK)
