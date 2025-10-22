from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, 'owner_id', None) == getattr(request.user, 'id', None)

class IsListingOwner(BasePermission):
    """Доступ только владельцу связанного listing."""
    def has_object_permission(self, request, view, obj):
        listing = getattr(obj, 'listing', None)
        owner_id = getattr(listing, 'owner_id', None)
        return request.user.is_authenticated and owner_id == getattr(request.user, 'id', None)
