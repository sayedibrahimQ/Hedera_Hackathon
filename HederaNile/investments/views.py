"""
Django REST Framework views for investments app.
"""
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta
from decimal import Decimal

from .models import Investment, AuditLog
from .serializers import (
    InvestmentCreateSerializer, InvestmentDetailSerializer,
    InvestmentListSerializer, InvestmentStatusSerializer,
    InvestmentTransactionSerializer, AuditLogSerializer,
    InvestmentStatsSerializer, LenderDashboardSerializer,
    StartupDashboardSerializer, AdminDashboardSerializer,
    BlockchainStatusSerializer, RefundRequestSerializer,
    EscrowReleaseSerializer, WalletConnectSerializer
)
from accounts.permissions import (
    IsAdminUser, IsLenderOrAdmin, IsOwnerOrAdmin, IsOwnerOrAdminOrReadOnly
)
from blockchain.services.hcs_service import log_event_to_hcs
from blockchain.services.escrow_service import deposit_funds, release_funds, get_escrow_balance
from blockchain.services.mirror_node_service import get_transaction, get_account_balance


class InvestmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for investment management.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'funding_request__startup__sector']
    search_fields = ['funding_request__title', 'funding_request__startup__name']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get investment queryset based on user permissions."""
        if self.request.user.role == 'ADMIN':
            return Investment.objects.all()
        elif self.request.user.role == 'LENDER':
            return Investment.objects.filter(lender=self.request.user)
        elif self.request.user.role == 'STARTUP':
            # Startups can see investments in their funding requests
            return Investment.objects.filter(funding_request__startup__owner=self.request.user)
        else:
            return Investment.objects.none()
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return InvestmentCreateSerializer
        elif self.action == 'list':
            return InvestmentListSerializer
        return InvestmentDetailSerializer
    
    def perform_create(self, serializer):
        """Create investment and initiate deposit process."""
        if self.request.user.role != 'LENDER':
            return Response(
                {'error': 'Only lenders can create investments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        investment = serializer.save(lender=self.request.user)
        
        # Update funding request current amount
        funding_request = investment.funding_request
        funding_request.current_amount += investment.amount
        
        # Check if funding goal is reached
        if funding_request.current_amount >= funding_request.total_amount:
            funding_request.status = 'FUNDED'
        
        funding_request.save(update_fields=['current_amount', 'status'])
        
        # Log investment to HCS
        try:
            if funding_request.hcs_topic_id:
                hcs_message_id = log_event_to_hcs(
                    topic_id=funding_request.hcs_topic_id,
                    event_type='DEPOSIT',
                    payload={
                        'investment_id': str(investment.id),
                        'lender_id': str(self.request.user.id),
                        'amount': str(investment.amount),
                        'funding_request_id': str(funding_request.id),
                        'timestamp': timezone.now().isoformat()
                    }
                )
                investment.hcs_deposit_message_id = hcs_message_id
                investment.save(update_fields=['hcs_deposit_message_id'])
        except Exception as e:
            print(f"HCS logging failed: {e}")
        
        # Log in audit trail
        AuditLog.objects.create(
            event_type='INVESTMENT_CREATED',
            user=self.request.user,
            payload={
                'investment_id': str(investment.id),
                'funding_request_id': str(funding_request.id),
                'amount': str(investment.amount)
            }
        )
    
    @action(detail=True, methods=['post'])
    def deposit_funds_blockchain(self, request, pk=None):
        """Deposit funds to escrow account (simulates wallet transaction)."""
        investment = self.get_object()
        
        # Check permissions
        if request.user != investment.lender and request.user.role != 'ADMIN':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check investment status
        if investment.status != 'PENDING':
            return Response(
                {'error': 'Only pending investments can be deposited'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Simulate deposit to custodial escrow
            tx_hash = deposit_funds(
                amount=investment.amount,
                metadata={
                    'investment_id': str(investment.id),
                    'lender_account': investment.lender.hedera_account_id,
                    'funding_request_id': str(investment.funding_request.id)
                }
            )
            
            # Update investment
            investment.status = 'DEPOSITED'
            investment.deposit_tx_hash = tx_hash
            investment.save(update_fields=['status', 'deposit_tx_hash'])
            
            return Response({
                'message': 'Funds deposited successfully',
                'transaction_hash': tx_hash,
                'investment': InvestmentDetailSerializer(investment).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Deposit failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def release_funds(self, request, pk=None):
        """Release funds to startup (admin only, after milestone verification)."""
        investment = self.get_object()
        serializer = EscrowReleaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        milestone_id = serializer.validated_data['milestone_id']
        release_amount = serializer.validated_data['release_amount']
        recipient_account = serializer.validated_data['recipient_account']
        admin_notes = serializer.validated_data.get('admin_notes', '')
        
        # Verify milestone exists and is verified
        from funding.models import Milestone
        try:
            milestone = Milestone.objects.get(
                id=milestone_id,
                funding_request=investment.funding_request,
                status='VERIFIED'
            )
        except Milestone.DoesNotExist:
            return Response(
                {'error': 'Milestone not found or not verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Release funds from escrow
            tx_hash = release_funds(
                to_account=recipient_account,
                amount=release_amount
            )
            
            # Update milestone
            milestone.status = 'RELEASED'
            milestone.release_tx_hash = tx_hash
            milestone.save(update_fields=['status', 'release_tx_hash'])
            
            # Update investment if fully released
            if release_amount >= investment.amount:
                investment.status = 'COMPLETED'
                investment.save(update_fields=['status'])
            
            # Log to HCS
            if investment.funding_request.hcs_topic_id:
                log_event_to_hcs(
                    topic_id=investment.funding_request.hcs_topic_id,
                    event_type='RELEASE_FUNDS',
                    payload={
                        'milestone_id': str(milestone_id),
                        'investment_id': str(investment.id),
                        'release_amount': str(release_amount),
                        'recipient_account': recipient_account,
                        'tx_hash': tx_hash,
                        'admin_id': str(request.user.id),
                        'timestamp': timezone.now().isoformat()
                    }
                )
            
            return Response({
                'message': 'Funds released successfully',
                'transaction_hash': tx_hash,
                'milestone': {
                    'id': milestone.id,
                    'status': milestone.status,
                    'release_tx_hash': tx_hash
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Fund release failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        """Request refund for investment."""
        investment = self.get_object()
        
        # Check permissions
        if request.user != investment.lender and request.user.role != 'ADMIN':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RefundRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reason = serializer.validated_data['reason']
        refund_amount = serializer.validated_data.get('refund_amount', investment.amount)
        
        # Log refund request
        AuditLog.objects.create(
            event_type='REFUND_REQUESTED',
            user=request.user,
            payload={
                'investment_id': str(investment.id),
                'reason': reason,
                'refund_amount': str(refund_amount)
            }
        )
        
        return Response({
            'message': 'Refund request submitted',
            'refund_amount': refund_amount,
            'status': 'pending_admin_review'
        })
    
    @action(detail=False, methods=['get'])
    def my_investments(self, request):
        """Get current lender's investments."""
        if request.user.role != 'LENDER':
            return Response(
                {'error': 'Only lenders can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        investments = Investment.objects.filter(lender=request.user)
        serializer = InvestmentListSerializer(investments, many=True)
        return Response(serializer.data)


class LenderDashboardAPIView(generics.RetrieveAPIView):
    """
    Lender dashboard data.
    GET /api/investments/lender-dashboard/
    """
    serializer_class = LenderDashboardSerializer
    permission_classes = [IsAuthenticated, IsLenderOrAdmin]
    
    def get(self, request, *args, **kwargs):
        """Get lender dashboard data."""
        user = request.user
        
        # Get investment statistics
        investments = Investment.objects.filter(lender=user)
        
        total_invested = investments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        active_investments = investments.filter(status='DEPOSITED').count()
        completed_investments = investments.filter(status='COMPLETED').count()
        
        # Calculate returns (simplified - based on completed investments)
        total_returns = Decimal('0')  # TODO: Implement actual return calculation
        
        # Portfolio performance
        portfolio_performance = 0.0  # TODO: Implement performance calculation
        
        # Recent investments
        recent_investments = investments.order_by('-created_at')[:5]
        
        # Investment distribution by sector
        investment_distribution = list(
            investments.values('funding_request__startup__sector')
            .annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
            .order_by('-total_amount')
        )
        
        dashboard_data = {
            'total_invested': total_invested,
            'active_investments': active_investments,
            'completed_investments': completed_investments,
            'total_returns': total_returns,
            'portfolio_performance': portfolio_performance,
            'recent_investments': recent_investments,
            'investment_distribution': investment_distribution
        }
        
        serializer = self.get_serializer(dashboard_data)
        return Response(serializer.data)


class StartupDashboardAPIView(generics.RetrieveAPIView):
    """
    Startup dashboard data.
    GET /api/investments/startup-dashboard/
    """
    serializer_class = StartupDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get startup dashboard data."""
        if request.user.role != 'STARTUP':
            return Response(
                {'error': 'Only startup users can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from startups.models import Startup
        from funding.models import FundingRequest, Milestone
        
        try:
            startup = Startup.objects.get(owner=request.user)
        except Startup.DoesNotExist:
            return Response({'error': 'No startup profile found'})
        
        # Get funding requests
        funding_requests = FundingRequest.objects.filter(startup=startup)
        
        total_funding_requests = funding_requests.count()
        total_amount_requested = funding_requests.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_amount_raised = funding_requests.aggregate(
            total=Sum('current_amount')
        )['total'] or Decimal('0')
        
        # Funding success rate
        funded_requests = funding_requests.filter(status__in=['FUNDED', 'ACTIVE', 'COMPLETED']).count()
        funding_success_rate = (funded_requests / total_funding_requests * 100) if total_funding_requests > 0 else 0
        
        # Milestones
        milestones = Milestone.objects.filter(funding_request__in=funding_requests)
        active_milestones = milestones.filter(status__in=['PENDING', 'IN_PROGRESS']).count()
        completed_milestones = milestones.filter(status='COMPLETED').count()
        
        # Recent investments in startup's projects
        recent_investments = Investment.objects.filter(
            funding_request__startup=startup
        ).order_by('-created_at')[:5]
        
        # Milestone progress
        milestone_progress = []
        for funding_request in funding_requests:
            request_milestones = funding_request.milestones.all()
            completed = request_milestones.filter(status='COMPLETED').count()
            total = request_milestones.count()
            milestone_progress.append({
                'funding_request_id': funding_request.id,
                'funding_request_title': funding_request.title,
                'completed_milestones': completed,
                'total_milestones': total,
                'progress_percentage': (completed / total * 100) if total > 0 else 0
            })
        
        dashboard_data = {
            'total_funding_requests': total_funding_requests,
            'total_amount_requested': total_amount_requested,
            'total_amount_raised': total_amount_raised,
            'funding_success_rate': round(funding_success_rate, 2),
            'active_milestones': active_milestones,
            'completed_milestones': completed_milestones,
            'recent_investments': recent_investments,
            'milestone_progress': milestone_progress
        }
        
        serializer = self.get_serializer(dashboard_data)
        return Response(serializer.data)


class AdminDashboardAPIView(generics.RetrieveAPIView):
    """
    Admin dashboard with platform-wide statistics.
    GET /api/investments/admin-dashboard/
    """
    serializer_class = AdminDashboardSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get admin dashboard data."""
        from django.contrib.auth import get_user_model
        from startups.models import Startup
        from funding.models import FundingRequest
        
        User = get_user_model()
        
        # Platform stats
        platform_stats = {
            'total_users': User.objects.count(),
            'total_startups': Startup.objects.count(),
            'total_funding_requests': FundingRequest.objects.count(),
            'total_investments': Investment.objects.count(),
            'total_volume': Investment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        }
        
        # User stats
        user_stats = {
            'startups': User.objects.filter(role='STARTUP').count(),
            'lenders': User.objects.filter(role='LENDER').count(),
            'admins': User.objects.filter(role='ADMIN').count(),
            'active_users_week': User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
        
        # Funding stats
        funding_stats = {
            'open_requests': FundingRequest.objects.filter(status='OPEN').count(),
            'funded_requests': FundingRequest.objects.filter(status='FUNDED').count(),
            'avg_funding_amount': FundingRequest.objects.aggregate(
                avg=Avg('total_amount')
            )['avg'] or Decimal('0')
        }
        
        # Investment stats
        investment_stats = {
            'pending_investments': Investment.objects.filter(status='PENDING').count(),
            'deposited_investments': Investment.objects.filter(status='DEPOSITED').count(),
            'completed_investments': Investment.objects.filter(status='COMPLETED').count(),
            'avg_investment_amount': Investment.objects.aggregate(
                avg=Avg('amount')
            )['avg'] or Decimal('0')
        }
        
        # Recent activities
        recent_activities = AuditLog.objects.order_by('-created_at')[:10]
        
        # Pending approvals
        pending_approvals = {
            'startup_approvals': Startup.objects.filter(onboarding_status='PENDING').count(),
            'milestone_verifications': 0  # TODO: Count pending milestone verifications
        }
        
        # System health
        system_health = {
            'database_status': 'healthy',
            'blockchain_status': 'healthy',  # TODO: Check actual Hedera status
            'ipfs_status': 'healthy'  # TODO: Check actual IPFS status
        }
        
        dashboard_data = {
            'platform_stats': platform_stats,
            'user_stats': user_stats,
            'funding_stats': funding_stats,
            'investment_stats': investment_stats,
            'recent_activities': recent_activities,
            'pending_approvals': pending_approvals,
            'system_health': system_health
        }
        
        serializer = self.get_serializer(dashboard_data)
        return Response(serializer.data)


class BlockchainStatusAPIView(generics.RetrieveAPIView):
    """
    Blockchain integration status.
    GET /api/investments/blockchain-status/
    """
    serializer_class = BlockchainStatusSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get blockchain status."""
        try:
            # Get escrow account balance
            escrow_balance = get_escrow_balance()
            
            # TODO: Implement actual status checks
            status_data = {
                'hedera_network_status': 'online',
                'mirror_node_status': 'online',
                'escrow_account_balance': escrow_balance,
                'hcs_topic_count': 0,  # TODO: Count HCS topics
                'recent_transactions': [],  # TODO: Get recent transactions
                'ipfs_status': 'online',
                'pinata_usage': {
                    'total_files': 0,
                    'storage_used': '0 MB'
                }
            }
            
            serializer = self.get_serializer(status_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get blockchain status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit log (read-only).
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'user']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get audit log entries."""
        return AuditLog.objects.all()


class WalletConnectAPIView(generics.CreateAPIView):
    """
    Verify wallet connection.
    POST /api/investments/wallet-connect/
    """
    serializer_class = WalletConnectSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Verify wallet connection."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        wallet_type = serializer.validated_data['wallet_type']
        account_id = serializer.validated_data['account_id']
        public_key = serializer.validated_data['public_key']
        network = serializer.validated_data['network']
        
        # Verify account_id matches user's Hedera account
        if account_id != request.user.hedera_account_id:
            return Response(
                {'error': 'Wallet account does not match user account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Verify public key matches account
        
        return Response({
            'message': 'Wallet connected successfully',
            'wallet_type': wallet_type,
            'account_id': account_id,
            'network': network
        })


class HealthCheckAPIView(generics.RetrieveAPIView):
    """
    Health check endpoint for the investments service.
    GET /api/investments/health/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Check service health."""
        return Response({
            'status': 'healthy',
            'service': 'investments',
            'timestamp': timezone.now().isoformat(),
            'total_investments': Investment.objects.count(),
            'active_investments': Investment.objects.filter(status='DEPOSITED').count()
        })