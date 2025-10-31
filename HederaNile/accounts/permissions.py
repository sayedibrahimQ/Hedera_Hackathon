"""
Custom permissions for the accounts app.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission that only allows admin users to access the view.
    """
    
    def has_permission(self, request, view):
        """Check if user is admin."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows owners of an object to edit it.
    Read-only permissions for any request.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access the object."""
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsStartupUser(permissions.BasePermission):
    """
    Permission that only allows startup users to access the view.
    """
    
    def has_permission(self, request, view):
        """Check if user is a startup."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'STARTUP'
        )


class IsLenderUser(permissions.BasePermission):
    """
    Permission that only allows lender users to access the view.
    """
    
    def has_permission(self, request, view):
        """Check if user is a lender."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'LENDER'
        )


class IsStartupOrAdmin(permissions.BasePermission):
    """
    Permission that allows startup users and admins to access the view.
    """
    
    def has_permission(self, request, view):
        """Check if user is startup or admin."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['STARTUP', 'ADMIN']
        )


class IsLenderOrAdmin(permissions.BasePermission):
    """
    Permission that allows lender users and admins to access the view.
    """
    
    def has_permission(self, request, view):
        """Check if user is lender or admin."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['LENDER', 'ADMIN']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows owners and admins to access the object.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access the object."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin can access everything
        if request.user.role == 'ADMIN':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            return obj == request.user


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read access to everyone, 
    but write access only to owners and admins.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access the object."""
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owners and admins
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin can modify everything
        if request.user.role == 'ADMIN':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            return obj == request.user