"""
Django REST Framework views for funding app.
"""
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta
from decimal import Decimal

from .models import FundingRequest, Milestone
from .serializers import (
    FundingRequestCreateSerializer, FundingRequestDetailSerializer,
    FundingRequestListSerializer, FundingRequestUpdateSerializer,
    FundingRequestStatusSerializer, MilestoneDetailSerializer,
    MilestoneUpdateSerializer, MilestoneProofSerializer,
    MilestoneVerificationSerializer, FundingStatsSerializer,
    MarketplaceFilterSerializer
)
from accounts.permissions import (
    IsAdminUser, IsStartupOrAdmin, IsOwnerOrAdmin, IsOwnerOrAdminOrReadOnly
)
from blockchain.services.hcs_service import create_hcs_topic, log_event_to_hcs
from ipfs_storage.services.storage_service import upload_file_to_ipfs


class FundingRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for funding request management.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'startup__sector', 'startup__country']
    search_fields = ['title', 'description', 'startup__name']
    ordering_fields = ['created_at', 'total_amount', 'current_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get funding request queryset based on user permissions."""
        if self.request.user.role == 'ADMIN':
            return FundingRequest.objects.all()
        elif self.request.user.role == 'STARTUP':
            return FundingRequest.objects.filter(startup__owner=self.request.user)
        else:  # LENDER
            # Lenders can see open funding requests from approved startups
            return FundingRequest.objects.filter(
                startup__onboarding_status='APPROVED',
                status__in=['OPEN', 'FUNDED']
            )
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return FundingRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FundingRequestUpdateSerializer
        elif self.action == 'list':
            return FundingRequestListSerializer
        elif self.action == 'retrieve':
            return FundingRequestDetailSerializer
        return FundingRequestDetailSerializer
    
    def perform_create(self, serializer):
        """Create funding request with HCS topic and log to blockchain."""
        # Get startup for current user
        try:
            from startups.models import Startup
            startup = Startup.objects.get(owner=self.request.user)
        except Startup.DoesNotExist:
            return Response(
                {'error': 'You must create a startup profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        funding_request = serializer.save(startup=startup)
        
        # Create HCS topic for this funding request
        try:
            topic_id = create_hcs_topic()
            funding_request.hcs_topic_id = topic_id
            funding_request.save(update_fields=['hcs_topic_id'])
            
            # Log creation event to HCS
            log_event_to_hcs(
                topic_id=topic_id,
                event_type='CREATE_REQUEST',
                payload={
                    'funding_request_id': str(funding_request.id),
                    'startup_id': str(startup.id),
                    'total_amount': str(funding_request.total_amount),
                    'milestone_count': funding_request.milestones.count(),
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            print(f"HCS topic creation failed: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update funding request status (admin only)."""
        funding_request = self.get_object()
        serializer = FundingRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = funding_request.status
        new_status = serializer.validated_data['status']
        
        funding_request.status = new_status
        funding_request.save(update_fields=['status'])
        
        # Log status change to HCS
        try:
            if funding_request.hcs_topic_id:
                log_event_to_hcs(
                    topic_id=funding_request.hcs_topic_id,
                    event_type='STATUS_UPDATE',
                    payload={
                        'funding_request_id': str(funding_request.id),
                        'old_status': old_status,
                        'new_status': new_status,
                        'admin_id': str(request.user.id),
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            print(f"HCS logging failed: {e}")
        
        # Log in audit trail
        from investments.models import AuditLog
        AuditLog.objects.create(
            event_type='FUNDING_STATUS_UPDATE',
            user=request.user,
            payload={
                'funding_request_id': str(funding_request.id),
                'old_status': old_status,
                'new_status': new_status
            }
        )
        
        return Response({
            'message': f'Funding request status updated from {old_status} to {new_status}',
            'funding_request': FundingRequestDetailSerializer(funding_request).data
        })
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current startup user's funding requests."""
        if request.user.role != 'STARTUP':
            return Response(
                {'error': 'Only startup users can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from startups.models import Startup
        try:
            startup = Startup.objects.get(owner=request.user)
            requests = FundingRequest.objects.filter(startup=startup)
            serializer = FundingRequestListSerializer(requests, many=True)
            return Response(serializer.data)
        except Startup.DoesNotExist:
            return Response([])
    
    @action(detail=True, methods=['get'])
    def milestones(self, request, pk=None):
        """Get milestones for funding request."""
        funding_request = self.get_object()
        milestones = funding_request.milestones.all().order_by('created_at')
        serializer = MilestoneDetailSerializer(milestones, many=True)
        return Response(serializer.data)


class MilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for milestone management.
    """
    serializer_class = MilestoneDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    
    def get_queryset(self):
        """Get milestone queryset based on user permissions."""
        if self.request.user.role == 'ADMIN':
            return Milestone.objects.all()
        elif self.request.user.role == 'STARTUP':
            return Milestone.objects.filter(funding_request__startup__owner=self.request.user)
        else:  # LENDER
            # Lenders can see milestones for projects they've invested in
            from investments.models import Investment
            invested_requests = Investment.objects.filter(
                lender=self.request.user
            ).values_list('funding_request_id', flat=True)
            return Milestone.objects.filter(funding_request_id__in=invested_requests)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return MilestoneUpdateSerializer
        return MilestoneDetailSerializer
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def submit_proof(self, request, pk=None):
        """Submit milestone proof (startup only)."""
        milestone = self.get_object()
        
        # Check permissions
        if (request.user.role != 'STARTUP' or 
            milestone.funding_request.startup.owner != request.user):
            return Response(
                {'error': 'Only the startup owner can submit proof'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check milestone status
        if milestone.status not in ['PENDING', 'IN_PROGRESS']:
            return Response(
                {'error': 'Proof can only be submitted for pending or in-progress milestones'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MilestoneProofSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        proof_file = serializer.validated_data['proof_file']
        description = serializer.validated_data['description']
        
        try:
            # Upload proof to IPFS
            cid = upload_file_to_ipfs(proof_file, {
                'milestone_id': str(milestone.id),
                'funding_request_id': str(milestone.funding_request.id),
                'proof_type': 'milestone_completion',
                'description': description,
                'uploaded_at': timezone.now().isoformat()
            })
            
            # Update milestone
            milestone.proof_ipfs_cid = cid
            milestone.status = 'COMPLETED'
            milestone.save(update_fields=['proof_ipfs_cid', 'status'])
            
            # Log to HCS
            try:
                if milestone.funding_request.hcs_topic_id:
                    log_event_to_hcs(
                        topic_id=milestone.funding_request.hcs_topic_id,
                        event_type='MILESTONE_PROOF_SUBMITTED',
                        payload={
                            'milestone_id': str(milestone.id),
                            'funding_request_id': str(milestone.funding_request.id),
                            'proof_cid': cid,
                            'description': description,
                            'timestamp': timezone.now().isoformat()
                        }
                    )
            except Exception as e:
                print(f"HCS logging failed: {e}")
            
            return Response({
                'message': 'Milestone proof submitted successfully',
                'milestone': MilestoneDetailSerializer(milestone).data,
                'proof_cid': cid
            })
            
        except Exception as e:
            return Response(
                {'error': f'Proof submission failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify_milestone(self, request, pk=None):
        """Verify milestone completion (admin only)."""
        milestone = self.get_object()
        serializer = MilestoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        verification_status = serializer.validated_data['verification_status']
        admin_notes = serializer.validated_data.get('admin_notes', '')
        
        if verification_status == 'VERIFIED':
            milestone.status = 'VERIFIED'
        else:  # REJECTED
            milestone.status = 'IN_PROGRESS'  # Back to in progress
        
        milestone.save(update_fields=['status'])
        
        # Log verification to HCS
        try:
            if milestone.funding_request.hcs_topic_id:
                hcs_message_id = log_event_to_hcs(
                    topic_id=milestone.funding_request.hcs_topic_id,
                    event_type='VERIFY_MILESTONE',
                    payload={
                        'milestone_id': str(milestone.id),
                        'verification_status': verification_status,
                        'admin_id': str(request.user.id),
                        'admin_notes': admin_notes,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                milestone.hcs_verify_message_id = hcs_message_id
                milestone.save(update_fields=['hcs_verify_message_id'])
        except Exception as e:
            print(f"HCS logging failed: {e}")
        
        return Response({
            'message': f'Milestone {verification_status.lower()}',
            'milestone': MilestoneDetailSerializer(milestone).data
        })


class FundingStatsAPIView(generics.RetrieveAPIView):
    """
    Get funding statistics for dashboard.
    GET /api/funding/stats/
    """
    serializer_class = FundingStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get funding statistics."""
        total_requests = FundingRequest.objects.count()
        active_requests = FundingRequest.objects.filter(status='OPEN').count()
        completed_requests = FundingRequest.objects.filter(status='COMPLETED').count()
        
        # Funding amounts
        total_requested = FundingRequest.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_funded = FundingRequest.objects.aggregate(
            total=Sum('current_amount')
        )['total'] or Decimal('0')
        
        # Average funding percentage
        funded_requests = FundingRequest.objects.filter(current_amount__gt=0)
        avg_funding_percentage = 0
        if funded_requests.exists():
            total_percentage = sum([
                (req.current_amount / req.total_amount) * 100
                for req in funded_requests
            ])
            avg_funding_percentage = total_percentage / funded_requests.count()
        
        # Top sectors
        top_sectors = list(
            FundingRequest.objects.values('startup__sector')
            .annotate(count=Count('startup__sector'))
            .order_by('-count')[:5]
        )
        
        # New requests this week
        week_ago = timezone.now() - timedelta(days=7)
        new_requests_week = FundingRequest.objects.filter(created_at__gte=week_ago).count()
        
        stats = {
            'total_requests': total_requests,
            'active_requests': active_requests,
            'completed_requests': completed_requests,
            'total_amount_requested': total_requested,
            'total_amount_funded': total_funded,
            'avg_funding_percentage': round(avg_funding_percentage, 2),
            'top_sectors': top_sectors,
            'new_requests_week': new_requests_week
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


class MarketplaceAPIView(generics.ListAPIView):
    """
    Marketplace view with filtering and search.
    GET /api/funding/marketplace/
    """
    serializer_class = FundingRequestListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'startup__sector', 'startup__country']
    search_fields = ['title', 'description', 'startup__name']
    ordering_fields = ['created_at', 'total_amount', 'current_amount', 'startup__credit_score']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get funding requests for marketplace."""
        return FundingRequest.objects.filter(
            startup__onboarding_status='APPROVED',
            status='OPEN'
        ).select_related('startup')
    
    def list(self, request, *args, **kwargs):
        """List funding requests with custom filtering."""
        # Apply custom filters
        queryset = self.get_queryset()
        
        # Custom filtering based on query parameters
        min_amount = request.query_params.get('min_amount')
        max_amount = request.query_params.get('max_amount')
        min_credit_score = request.query_params.get('min_credit_score')
        
        if min_amount:
            queryset = queryset.filter(total_amount__gte=Decimal(min_amount))
        
        if max_amount:
            queryset = queryset.filter(total_amount__lte=Decimal(max_amount))
        
        if min_credit_score:
            queryset = queryset.filter(startup__credit_score__gte=int(min_credit_score))
        
        # Apply standard filtering and pagination
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HealthCheckAPIView(generics.RetrieveAPIView):
    """
    Health check endpoint for the funding service.
    GET /api/funding/health/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Check service health."""
        return Response({
            'status': 'healthy',
            'service': 'funding',
            'timestamp': timezone.now().isoformat(),
            'total_requests': FundingRequest.objects.count(),
            'active_requests': FundingRequest.objects.filter(status='OPEN').count()
        })