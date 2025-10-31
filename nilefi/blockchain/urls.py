from django.urls import path
from .views import OFDWalletView

urlpatterns = [
    path('wallet/', OFDWalletView.as_view(), name='blockchain-wallet'),
]
