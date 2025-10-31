# NileFi MVP - REST API Documentation

## Overview

The NileFi MVP provides a comprehensive REST API for blockchain-based SME lending platform operations. All endpoints require authentication except where noted.

**Base URL**: `http://localhost:8000/api/`
**Authentication**: JWT Bearer tokens via wallet signature verification

## Authentication Endpoints

### POST /api/auth/nonce/
Generate authentication nonce for wallet signature.
```json
{
  "hedera_account_id": "0.0.7143910"
}
```

### POST /api/auth/wallet/
Authenticate with wallet signature.
```json
{
  "hedera_account_id": "0.0.7143910",
  "signature": "wallet_signature",
  "nonce": "generated_nonce"
}
```

### POST /api/auth/register/
Complete user profile after authentication.
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "STARTUP",
  "profile_meta": {}
}
```

### POST /api/auth/logout/
Logout and blacklist refresh token.

### GET /api/auth/stats/
Get user statistics (admin only).

## User Management (ViewSet)

### GET /api/users/
List users (admin) or current user profile.

### POST /api/users/
Create user profile.

### GET /api/users/{id}/
Retrieve user profile.

### PUT/PATCH /api/users/{id}/
Update user profile.

### GET /api/users/me/
Get current user profile.

### PUT /api/users/update_profile/
Update current user profile.

### POST /api/users/{id}/update_role/
Update user role (admin only).

## Startup Management (ViewSet)

### GET /api/startups/
List startups (filtered by role).

### POST /api/startups/
Create startup profile.

### GET /api/startups/{id}/
Retrieve startup details.

### PUT/PATCH /api/startups/{id}/
Update startup profile.

### DELETE /api/startups/{id}/
Delete startup profile.

### POST /api/startups/{id}/update_onboarding_status/
Update onboarding status (admin only).
```json
{
  "onboarding_status": "APPROVED"
}
```

### POST /api/startups/{id}/recalculate_score/
Recalculate AI credit score.

### POST /api/startups/{id}/upload_document/
Upload document to IPFS.
```form-data
file: document_file
document_type: "business_plan"
description: "Updated business plan"
```

### GET /api/startups/my_startup/
Get current user's startup profile.

### GET /api/startups/marketplace/
Public marketplace of approved startups.

### GET /api/startups/public/{id}/
Public view of approved startup.

### GET /api/startups/stats/
Startup statistics (admin only).

## Funding Management (ViewSet)

### GET /api/funding-requests/
List funding requests (filtered by role).

### POST /api/funding-requests/
Create funding request with milestones.
```json
{
  "title": "Expand Operations",
  "description": "Need funding to expand...",
  "total_amount": "50000.00",
  "milestones": [
    {
      "title": "Phase 1",
      "description": "Initial setup",
      "target_amount": "25000.00",
      "percentage": 50,
      "due_date": "2024-06-01"
    }
  ]
}
```

### GET /api/funding-requests/{id}/
Retrieve funding request details.

### PUT/PATCH /api/funding-requests/{id}/
Update funding request.

### DELETE /api/funding-requests/{id}/
Delete funding request.

### POST /api/funding-requests/{id}/update_status/
Update funding request status (admin only).

### GET /api/funding-requests/my_requests/
Get current startup's funding requests.

### GET /api/funding-requests/{id}/milestones/
Get milestones for funding request.

### GET /api/funding/marketplace/
Advanced marketplace with filtering.
Query parameters: `search`, `sector`, `country`, `min_amount`, `max_amount`, `status`, `min_credit_score`, `ordering`

### GET /api/funding/stats/
Funding statistics.

## Milestone Management (ViewSet)

### GET /api/milestones/
List milestones (filtered by role).

### GET /api/milestones/{id}/
Retrieve milestone details.

### PUT/PATCH /api/milestones/{id}/
Update milestone.

### POST /api/milestones/{id}/submit_proof/
Submit milestone completion proof.
```form-data
proof_file: proof_document
description: "Milestone completed as planned"
```

### POST /api/milestones/{id}/verify_milestone/
Verify milestone completion (admin only).
```json
{
  "verification_status": "VERIFIED",
  "admin_notes": "Milestone successfully completed"
}
```

## Investment Management (ViewSet)

### GET /api/investments/
List investments (filtered by role).

### POST /api/investments/
Create investment.
```json
{
  "funding_request": "funding_request_uuid",
  "amount": "5000.00"
}
```

### GET /api/investments/{id}/
Retrieve investment details.

### PUT/PATCH /api/investments/{id}/
Update investment.

### POST /api/investments/{id}/deposit_funds_blockchain/
Deposit funds to escrow account.

### POST /api/investments/{id}/release_funds/
Release funds to startup (admin only).
```json
{
  "milestone_id": "milestone_uuid",
  "release_amount": "5000.00",
  "recipient_account": "0.0.startup_account",
  "admin_notes": "Milestone verified"
}
```

### POST /api/investments/{id}/request_refund/
Request investment refund.
```json
{
  "reason": "Project cancelled",
  "refund_amount": "5000.00"
}
```

### GET /api/investments/my_investments/
Get current lender's investments.

## Dashboard Endpoints

### GET /api/investments/lender-dashboard/
Lender dashboard data.
```json
{
  "total_invested": "25000.00",
  "active_investments": 3,
  "completed_investments": 2,
  "total_returns": "2500.00",
  "portfolio_performance": 10.5,
  "recent_investments": [...],
  "investment_distribution": [...]
}
```

### GET /api/investments/startup-dashboard/
Startup dashboard data.
```json
{
  "total_funding_requests": 2,
  "total_amount_requested": "100000.00",
  "total_amount_raised": "75000.00",
  "funding_success_rate": 75.0,
  "active_milestones": 3,
  "completed_milestones": 5,
  "recent_investments": [...],
  "milestone_progress": [...]
}
```

### GET /api/investments/admin-dashboard/
Admin dashboard with platform-wide statistics.
```json
{
  "platform_stats": {...},
  "user_stats": {...},
  "funding_stats": {...},
  "investment_stats": {...},
  "recent_activities": [...],
  "pending_approvals": {...},
  "system_health": {...}
}
```

## Blockchain Integration

### GET /api/investments/blockchain-status/
Blockchain integration status (admin only).
```json
{
  "hedera_network_status": "online",
  "mirror_node_status": "online",
  "escrow_account_balance": "50000.00",
  "hcs_topic_count": 25,
  "recent_transactions": [...],
  "ipfs_status": "online",
  "pinata_usage": {...}
}
```

### POST /api/investments/wallet-connect/
Verify wallet connection.
```json
{
  "wallet_type": "HashPack",
  "account_id": "0.0.7143910",
  "public_key": "wallet_public_key",
  "network": "testnet"
}
```

## Audit Log (ViewSet)

### GET /api/audit-logs/
List audit log entries (admin only).
Filterable by: `event_type`, `user`

## Health Checks

### GET /api/auth/health/
Authentication service health.

### GET /api/startups/health/
Startups service health.

### GET /api/funding/health/
Funding service health.

### GET /api/investments/health/
Investments service health.

## JWT Token Management

### POST /api/auth/token/refresh/
Refresh access token.
```json
{
  "refresh": "refresh_token"
}
```

### POST /api/auth/token/verify/
Verify token validity.
```json
{
  "token": "access_token"
}
```

## Response Formats

### Success Response
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "code": "error_code"
}
```

### Validation Error Response
```json
{
  "field1": ["This field is required."],
  "field2": ["Invalid value."]
}
```

## Pagination

List endpoints support pagination:
```json
{
  "count": 100,
  "next": "http://api.example.org/accounts/?page=4",
  "previous": "http://api.example.org/accounts/?page=2",
  "results": [...]
}
```

## Filtering and Search

Most list endpoints support:
- **Search**: `?search=query`
- **Filtering**: `?field=value`
- **Ordering**: `?ordering=field` or `?ordering=-field`

## Permission Levels

- **Public**: No authentication required
- **Authenticated**: Valid JWT token required
- **Owner**: Resource owner or admin
- **Startup**: STARTUP role required
- **Lender**: LENDER role required
- **Admin**: ADMIN role required

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **General API**: 100 requests per minute
- **Upload endpoints**: 10 requests per minute

## Error Codes

- **400**: Bad Request - Invalid input data
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - Server error

## WebSocket Endpoints (Future)

Real-time updates for:
- Investment notifications
- Milestone status changes
- Admin approvals
- Blockchain transaction confirmations