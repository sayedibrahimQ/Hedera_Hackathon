from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, SetWalletView, KYCUploadView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='accounts-register'),
    path('login/', TokenObtainPairView.as_view(), name='accounts-token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='accounts-token-refresh'),
    path('me/', UserProfileView.as_view(), name='accounts-me'),
    path('set-wallet/', SetWalletView.as_view(), name='accounts-set-wallet'),
    path('kyc-upload/', KYCUploadView.as_view(), name='accounts-kyc-upload'),
]
