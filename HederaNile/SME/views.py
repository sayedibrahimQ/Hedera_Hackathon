"""
Django REST Framework views for startups app.
"""
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta

from .models import Startup
from .serializers import (
    StartupCreateSerializer, StartupUpdateSerializer, StartupDetailSerializer,
    StartupListSerializer, StartupPublicSerializer, StartupOnboardingSerializer,
    StartupScoringSerializer, StartupStatsSerializer, DocumentUploadSerializer
)
from accounts.permissions import (
    IsAdminUser, IsStartupOrAdmin, IsOwnerOrAdmin, IsOwnerOrAdminOrReadOnly
)
from scoring.services.scoring_service import calculate_credit_score
from ipfs_storage.services.storage_service import upload_file_to_ipfs
from blockchain.services.hcs_service import log_event_to_hcs


class StartupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for startup profile management.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'country', 'onboarding_status']
    search_fields = ['name', 'description', 'sector']
    ordering_fields = ['created_at', 'credit_score', 'revenue']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get startup queryset based on user permissions."""
        if self.request.user.role == 'ADMIN':
            return Startup.objects.all()
        elif self.request.user.role == 'STARTUP':
            return Startup.objects.filter(owner=self.request.user)
        else:  # LENDER
            # Lenders can only see approved startups
            return Startup.objects.filter(onboarding_status='APPROVED')
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return StartupCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StartupUpdateSerializer
        elif self.action == 'list':
            return StartupListSerializer
        elif self.action == 'retrieve':
            return StartupDetailSerializer
        return StartupDetailSerializer
    
    def perform_create(self, serializer):
        """Create startup profile and calculate initial credit score."""
        startup = serializer.save(owner=self.request.user)
        
        # Calculate initial credit score
        try:
            scoring_result = calculate_credit_score({
                'revenue': float(startup.revenue),
                'monthly_sales': float(startup.monthly_sales),
                'business_age': startup.business_age,
                'sector': startup.sector,
                'docs_uploaded': len(startup.ipfs_docs) if startup.ipfs_docs else 0
            })
            
            startup.credit_score = scoring_result['score']
            startup.save(update_fields=['credit_score'])
        except Exception as e:
            # If scoring fails, continue without score
            print(f"Credit scoring failed: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_onboarding_status(self, request, pk=None):
        """Update startup onboarding status (admin only)."""
        startup = self.get_object()
        serializer = StartupOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = startup.onboarding_status
        new_status = serializer.validated_data['onboarding_status']
        
        startup.onboarding_status = new_status
        startup.save(update_fields=['onboarding_status'])
        
        # Log status change to HCS
        try:
            hcs_message_id = log_event_to_hcs(
                topic_id=startup.hcs_create_message_id,  # Use existing topic
                event_type='STATUS_UPDATE',
                payload={
                    'startup_id': str(startup.id),
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
            event_type='STARTUP_STATUS_UPDATE',
            user=request.user,
            payload={
                'startup_id': str(startup.id),
                'old_status': old_status,
                'new_status': new_status
            }
        )
        
        return Response({
            'message': f'Startup status updated from {old_status} to {new_status}',
            'startup': StartupDetailSerializer(startup).data
        })
    
    @action(detail=True, methods=['post'])
    def recalculate_score(self, request, pk=None):
        """Recalculate credit score for startup."""
        startup = self.get_object()
        
        # Check permissions
        if request.user.role not in ['ADMIN'] and startup.owner != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            scoring_result = calculate_credit_score({
                'revenue': float(startup.revenue),
                'monthly_sales': float(startup.monthly_sales),
                'business_age': startup.business_age,
                'sector': startup.sector,
                'docs_uploaded': len(startup.ipfs_docs) if startup.ipfs_docs else 0
            })
            
            old_score = startup.credit_score
            startup.credit_score = scoring_result['score']
            startup.save(update_fields=['credit_score'])
            
            scoring_data = {
                'startup_id': startup.id,
                'score': scoring_result['score'],
                'risk_bucket': scoring_result['risk_bucket'],
                'feature_importance': scoring_result['feature_importance'],
                'explanation': scoring_result['explanation'],
                'scoring_date': timezone.now()
            }
            
            return Response({
                'message': f'Credit score updated from {old_score} to {scoring_result["score"]}',
                'scoring': StartupScoringSerializer(scoring_data).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Credit scoring failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_document(self, request, pk=None):
        """Upload document to IPFS for startup."""
        startup = self.get_object()
        
        # Check permissions
        if request.user.role not in ['ADMIN'] and startup.owner != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        document_type = serializer.validated_data['document_type']
        description = serializer.validated_data.get('description', '')
        
        try:
            # Upload to IPFS
            cid = upload_file_to_ipfs(file, {
                'startup_id': str(startup.id),
                'document_type': document_type,
                'description': description,
                'uploaded_at': timezone.now().isoformat()
            })
            
            # Add to startup's IPFS docs
            if not startup.ipfs_docs:
                startup.ipfs_docs = []
            
            startup.ipfs_docs.append({
                'cid': cid,
                'filename': file.name,
                'document_type': document_type,
                'description': description,
                'uploaded_at': timezone.now().isoformat()
            })
            
            startup.save(update_fields=['ipfs_docs'])
            
            # Recalculate credit score with new document count
            try:
                scoring_result = calculate_credit_score({
                    'revenue': float(startup.revenue),
                    'monthly_sales': float(startup.monthly_sales),
                    'business_age': startup.business_age,
                    'sector': startup.sector,
                    'docs_uploaded': len(startup.ipfs_docs)
                })
                
                startup.credit_score = scoring_result['score']
                startup.save(update_fields=['credit_score'])
            except Exception as e:
                print(f"Credit score recalculation failed: {e}")
            
            return Response({
                'message': 'Document uploaded successfully',
                'cid': cid,
                'document': {
                    'cid': cid,
                    'filename': file.name,
                    'document_type': document_type,
                    'description': description
                },
                'new_credit_score': startup.credit_score
            })
            
        except Exception as e:
            return Response(
                {'error': f'Document upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_startup(self, request):
        """Get current user's startup profile."""
        if request.user.role != 'STARTUP':
            return Response(
                {'error': 'Only startup users can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            startup = Startup.objects.get(owner=request.user)
            serializer = StartupDetailSerializer(startup)
            return Response(serializer.data)
        except Startup.DoesNotExist:
            return Response(
                {'error': 'No startup profile found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )


class StartupStatsAPIView(generics.RetrieveAPIView):
    """
    Get startup statistics for admin dashboard.
    GET /api/startups/stats/
    """
    serializer_class = StartupStatsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get startup statistics."""
        total_startups = Startup.objects.count()
        pending_approval = Startup.objects.filter(onboarding_status='PENDING').count()
        approved_startups = Startup.objects.filter(onboarding_status='APPROVED').count()
        rejected_startups = Startup.objects.filter(onboarding_status='REJECTED').count()
        
        # Average credit score
        avg_credit_score = Startup.objects.aggregate(
            avg_score=Avg('credit_score')
        )['avg_score'] or 0
        
        # Top sectors
        top_sectors = list(
            Startup.objects.values('sector')
            .annotate(count=Count('sector'))
            .order_by('-count')[:5]
        )
        
        # New startups this week
        week_ago = timezone.now() - timedelta(days=7)
        new_startups_week = Startup.objects.filter(created_at__gte=week_ago).count()
        
        stats = {
            'total_startups': total_startups,
            'pending_approval': pending_approval,
            'approved_startups': approved_startups,
            'rejected_startups': rejected_startups,
            'avg_credit_score': round(avg_credit_score, 2),
            'top_sectors': top_sectors,
            'new_startups_week': new_startups_week
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


class StartupMarketplaceAPIView(generics.ListAPIView):
    """
    Public marketplace view of approved startups.
    GET /api/startups/marketplace/
    """
    serializer_class = StartupListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'country']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'credit_score', 'revenue']
    ordering = ['-credit_score']
    
    def get_queryset(self):
        """Get approved startups for marketplace."""
        return Startup.objects.filter(onboarding_status='APPROVED')


class StartupDetailPublicAPIView(generics.RetrieveAPIView):
    """
    Public detail view of approved startup.
    GET /api/startups/public/{id}/
    """
    serializer_class = StartupDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get approved startups for public view."""
        return Startup.objects.filter(onboarding_status='APPROVED')


class HealthCheckAPIView(generics.RetrieveAPIView):
    """
    Health check endpoint for the startups service.
    GET /api/startups/health/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Check service health."""
        return Response({
            'status': 'healthy',
            'service': 'startups',
            'timestamp': timezone.now().isoformat(),
            'total_startups': Startup.objects.count(),
            'approved_startups': Startup.objects.filter(onboarding_status='APPROVED').count()
        })