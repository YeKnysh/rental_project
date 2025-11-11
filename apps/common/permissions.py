# apps/common/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

__all__ = [
    "IsOwnerOrReadOnly",
    "IsListingOwner",
    "IsTenantOrReadOnly",
    "IsAuthorOrReadOnly",
]


class IsOwnerOrReadOnly(BasePermission):
    """
    Read: allowed to anyone.
    Write: only the object owner.

    The object is expected to expose `owner_id` (or `owner.id` as a fallback).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        owner_id = getattr(obj, "owner_id", None)
        if owner_id is None:
            owner = getattr(obj, "owner", None)
            owner_id = getattr(owner, "id", None)

        return bool(request.user.is_authenticated and owner_id == getattr(request.user, "id", None))


class IsListingOwner(BasePermission):
    """
    Write permission for the owner of the related listing.

    The object is expected to have `listing` with `owner_id`.
    Typically used for booking actions like confirm/decline.
    """
    def has_object_permission(self, request, view, obj):
        # For safety, allow safe methods to pass through if applied broadly.
        if request.method in SAFE_METHODS:
            return True

        listing = getattr(obj, "listing", None)
        owner_id = getattr(listing, "owner_id", None)
        return bool(request.user.is_authenticated and owner_id == getattr(request.user, "id", None))


class IsTenantOrReadOnly(BasePermission):
    """
    Read: allowed to anyone.
    Write: only the tenant (the user who owns the record through `tenant_id`).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and getattr(obj, "tenant_id", None) == request.user.id)


class IsAuthorOrReadOnly(BasePermission):
    """
    Read: allowed to anyone.
    Write: only the author (the user referenced by `author_id`).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and getattr(obj, "author_id", None) == request.user.id)
