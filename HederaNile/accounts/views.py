"""
Django REST Framework views for accounts app.
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib
import jwt
from django.conf import settings

from .models import AuthNonce
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserPublicSerializer,
    AuthNonceSerializer, WalletAuthSerializer, PasswordResetSerializer,
    RoleUpdateSerializer, UserStatsSerializer
)
from .permissions import IsAdminUser, IsOwnerOrReadOnly


User = get_user_model()


class AuthNonceAPIView(generics.CreateAPIView):
    """
    Generate authentication nonce for wallet signature.
    POST /api/auth/nonce/
    """
    serializer_class = AuthNonceSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Generate nonce for wallet authentication."""
        hedera_account_id = request.data.get('hedera_account_id')
        
        if not hedera_account_id:
            return Response(
                {'error': 'hedera_account_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clean up expired nonces
        AuthNonce.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        # Generate new nonce
        nonce_value = secrets.token_hex(32)
        
        # Remove existing nonce for this account
        AuthNonce.objects.filter(hedera_account_id=hedera_account_id).delete()
        
        # Create new nonce
        auth_nonce = AuthNonce.objects.create(
            hedera_account_id=hedera_account_id,
            nonce=nonce_value
        )
        
        serializer = self.get_serializer(auth_nonce)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WalletAuthAPIView(generics.CreateAPIView):
    """
    Authenticate user with wallet signature.
    POST /api/auth/wallet/
    """
    serializer_class = WalletAuthSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Authenticate user with wallet signature."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hedera_account_id = serializer.validated_data['hedera_account_id']
        signature = serializer.validated_data['signature']
        nonce = serializer.validated_data['nonce']
        
        try:
            # Verify nonce exists and is valid
            auth_nonce = AuthNonce.objects.get(
                hedera_account_id=hedera_account_id,
                nonce=nonce,
                expires_at__gt=timezone.now()
            )
        except AuthNonce.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired nonce'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement Hedera signature verification
        # This would verify the signature against the nonce using the user's public key
        # For MVP, we'll assume signature is valid if nonce exists
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                hedera_account_id=hedera_account_id,
                defaults={
                    'name': f'User {hedera_account_id}',
                    'email': f'{hedera_account_id}@temp.nilefi.com',
                    'role': 'STARTUP'  # Default role
                }
            )
            
            # Delete used nonce
            auth_nonce.delete()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user).data,
                'is_new_user': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Complete user registration after wallet auth.
    POST /api/auth/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Complete user profile registration."""
        # Update existing user with profile data
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_200_OK
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profile management.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Get user queryset based on permissions."""
        if self.request.user.role == 'ADMIN':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action in ['list', 'retrieve']:
            return UserProfileSerializer
        return UserProfileSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_role(self, request, pk=None):
        """Update user role (admin only)."""
        user = self.get_object()
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_role = user.role
        new_role = serializer.validated_data['new_role']
        reason = serializer.validated_data.get('reason', '')
        
        user.role = new_role
        user.save(update_fields=['role'])
        
        # Log role change in audit log
        from investments.models import AuditLog
        AuditLog.objects.create(
            event_type='ROLE_UPDATE',
            user=request.user,
            payload={
                'target_user_id': str(user.id),
                'old_role': old_role,
                'new_role': new_role,
                'reason': reason
            }
        )
        
        return Response({
            'message': f'User role updated from {old_role} to {new_role}',
            'user': UserProfileSerializer(user).data
        })


class UserStatsAPIView(generics.RetrieveAPIView):
    """
    Get user statistics for admin dashboard.
    GET /api/users/stats/
    """
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get user statistics."""
        total_users = User.objects.count()
        startups = User.objects.filter(role='STARTUP').count()
        lenders = User.objects.filter(role='LENDER').count()
        admins = User.objects.filter(role='ADMIN').count()
        
        # Users registered today
        today = timezone.now().date()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        
        # Users registered this week
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        
        # Active users this week (logged in within 7 days)
        active_users_week = User.objects.filter(last_login__gte=week_ago).count()
        
        stats = {
            'total_users': total_users,
            'startups': startups,
            'lenders': lenders,
            'admins': admins,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'active_users_week': active_users_week
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


class LogoutAPIView(generics.CreateAPIView):
    """
    Logout user by blacklisting refresh token.
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Logout user."""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetAPIView(generics.CreateAPIView):
    """
    Reset password using wallet signature (for emergency access).
    POST /api/auth/reset-password/
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Reset user access with wallet signature."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hedera_account_id = serializer.validated_data['hedera_account_id']
        new_signature = serializer.validated_data['new_signature']
        nonce = serializer.validated_data['nonce']
        
        try:
            # Verify nonce
            auth_nonce = AuthNonce.objects.get(
                hedera_account_id=hedera_account_id,
                nonce=nonce,
                expires_at__gt=timezone.now()
            )
            
            # Get user
            user = User.objects.get(hedera_account_id=hedera_account_id)
            
            # TODO: Verify new signature
            # This would implement signature verification for password reset
            
            # Delete nonce
            auth_nonce.delete()
            
            # Generate new tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'message': 'Password reset successful'
            })
            
        except (AuthNonce.DoesNotExist, User.DoesNotExist):
            return Response(
                {'error': 'Invalid nonce or user not found'},
                status=status.HTTP_400_BAD_REQUEST
            )


class HealthCheckAPIView(generics.RetrieveAPIView):
    """
    Health check endpoint for the accounts service.
    GET /api/auth/health/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Check service health."""
        return Response({
            'status': 'healthy',
            'service': 'accounts',
            'timestamp': timezone.now().isoformat(),
            'total_users': User.objects.count()
        })