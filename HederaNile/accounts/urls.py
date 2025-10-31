"""
URL configuration for accounts app.
"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
from .views import (
    AuthNonceAPIView, WalletAuthAPIView, UserRegistrationAPIView,
    UserStatsAPIView, LogoutAPIView, PasswordResetAPIView,
    HealthCheckAPIView
)

# Frontend Views
def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

def profile_view(request):
    return render(request, 'accounts/profile.html')  # Placeholder

def settings_view(request):
    return render(request, 'accounts/settings.html')  # Placeholder

app_name = 'accounts'

urlpatterns = [
    # Frontend routes
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', login_required(profile_view), name='profile'),
    path('settings/', login_required(settings_view), name='settings'),
    
    # Authentication API endpoints
    path('nonce/', AuthNonceAPIView.as_view(), name='auth-nonce'),
    path('wallet/', WalletAuthAPIView.as_view(), name='wallet-auth'),
    path('api/register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('reset-password/', PasswordResetAPIView.as_view(), name='password-reset'),
    
    # User statistics (admin)
    path('stats/', UserStatsAPIView.as_view(), name='user-stats'),
    
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]