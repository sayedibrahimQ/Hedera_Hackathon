"""
URL configuration for funding app.
"""
from django.urls import path
from .views import (
    FundingStatsAPIView, MarketplaceAPIView, HealthCheckAPIView
)

app_name = 'fund'

urlpatterns = [
    # Funding statistics
    path('stats/', FundingStatsAPIView.as_view(), name='funding-stats'),
    
    # Marketplace with advanced filtering
    path('marketplace/', MarketplaceAPIView.as_view(), name='funding-marketplace'),
    
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]

# Note: CRUD operations for funding requests and milestones are handled by the router in main urls.py
# Additional endpoints:
# - POST /api/funding-requests/{id}/update_status/ (admin)
# - GET /api/funding-requests/my_requests/ (startup)
# - GET /api/funding-requests/{id}/milestones/
# - POST /api/milestones/{id}/submit_proof/ (startup)
# - POST /api/milestones/{id}/verify_milestone/ (admin)