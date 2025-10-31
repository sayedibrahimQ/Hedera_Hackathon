"""
URL configuration for investments app.
"""
from django.urls import path
from .views import (
    LenderDashboardAPIView, StartupDashboardAPIView, AdminDashboardAPIView,
    BlockchainStatusAPIView, WalletConnectAPIView, HealthCheckAPIView
)

app_name = 'investments'

urlpatterns = [
    # Dashboard endpoints
    path('lender-dashboard/', LenderDashboardAPIView.as_view(), name='lender-dashboard'),
    path('startup-dashboard/', StartupDashboardAPIView.as_view(), name='startup-dashboard'),
    path('admin-dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    
    # Blockchain integration
    path('blockchain-status/', BlockchainStatusAPIView.as_view(), name='blockchain-status'),
    path('wallet-connect/', WalletConnectAPIView.as_view(), name='wallet-connect'),
    
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]

# Note: CRUD operations for investments are handled by the router in main urls.py
# Additional endpoints:
# - POST /api/investments/{id}/deposit_funds_blockchain/
# - POST /api/investments/{id}/release_funds/ (admin)
# - POST /api/investments/{id}/request_refund/
# - GET /api/investments/my_investments/ (lender)