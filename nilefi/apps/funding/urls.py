from django.urls import path
from .views import (
    LoanRequestListCreateView,
    LoanRequestDetailView,
    BrowseLoanRequestsView,
    FundLoanView,
    RepayLoanView,
    UserLoansView,
    ReleaseFundsView
)

urlpatterns = [
    path('requests/', LoanRequestListCreateView.as_view(), name='funding-loan-requests'),
    path('requests/<int:pk>/', LoanRequestDetailView.as_view(), name='funding-loan-request-detail'),
    path('browse/', BrowseLoanRequestsView.as_view(), name='funding-browse-loans'),
    path('fund/<int:pk>/', FundLoanView.as_view(), name='funding-fund-loan'),
    path('repay/<int:pk>/', RepayLoanView.as_view(), name='funding-repay-loan'),
    path('my-loans/', UserLoansView.as_view(), name='funding-user-loans'),
    path('release-funds/<int:pk>/', ReleaseFundsView.as_view(), name='funding-release-funds'),
]
