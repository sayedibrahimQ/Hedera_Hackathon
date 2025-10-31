"""
URL configuration for startups app.
"""
from django.urls import path
from .views import (
    StartupStatsAPIView, StartupMarketplaceAPIView,
    StartupDetailPublicAPIView, HealthCheckAPIView
)

app_name = 'SME'

urlpatterns = [
    # Startup statistics (admin)
    path('stats/', StartupStatsAPIView.as_view(), name='startup-stats'),
    
    # Public marketplace
    path('marketplace/', StartupMarketplaceAPIView.as_view(), name='startup-marketplace'),
    path('public/<uuid:pk>/', StartupDetailPublicAPIView.as_view(), name='startup-public-detail'),
    
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]

# Note: CRUD operations for startups are handled by the router in main urls.py
# Additional endpoints:
# - POST /api/startups/{id}/update_onboarding_status/ (admin)
# - POST /api/startups/{id}/recalculate_score/
# - POST /api/startups/{id}/upload_document/
# - GET /api/startups/my_startup/