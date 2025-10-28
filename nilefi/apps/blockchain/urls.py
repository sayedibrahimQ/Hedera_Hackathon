
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from nilefi.apps.blockchain.views import (
    AccountViewSet,
    TokenizationViewSet,
    RentalAgreementViewSet,
)

router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="accounts")
router.register(r"tokenize", TokenizationViewSet, basename="tokenize")
router.register(
    r"rental-agreements", RentalAgreementViewSet, basename="rental-agreements"
)

urlpatterns = [
    path("", include(router.urls)),
]
