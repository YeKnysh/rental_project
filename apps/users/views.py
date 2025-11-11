# apps/users/views.py
"""
Users API.

Routes (mounted under /api/v1/ via DefaultRouter):
  - POST /api/v1/users/register/  — register a new user, auto-add to "customer" group, start session
  - GET  /api/v1/users/me/        — return current authenticated user (session-based)
"""
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from .serializers import RegisterSerializer, UserPublicSerializer

User = get_user_model()


@extend_schema_view(
    register=extend_schema(
        tags=["users"],
        summary="Register a new user (session login)",
        description=(
            "Creates a new user (default role: **customer**) and logs them in via **session**. "
            "Returns a public profile of the newly created user. "
            "Cookie `sessionid` will be set on success."
        ),
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=UserPublicSerializer,
                description="User created & logged in",
            ),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Request",
                value={"email": "user@example.com", "password": "StrongPass_123"},
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "id": 71,
                    "email": "user@example.com",
                    "first_name": "",
                    "last_name": "",
                    "is_staff": False,
                },
                response_only=True,
            ),
        ],
    ),
    me=extend_schema(
        tags=["users"],
        summary="Get current user profile",
        description="Returns public profile of the **currently authenticated** user.",
        responses={200: UserPublicSerializer, 401: OpenApiResponse(description="Not authenticated")},
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 71,
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_staff": False,
                },
                response_only=True,
            )
        ],
    ),
)
class UsersViewSet(viewsets.ViewSet):
    """
    Minimal Users API:
    - `register` is open for everyone (no auth).
    - `me` requires an authenticated session (login through /api-auth/login/ or Swagger cookieAuth).
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request: Request) -> Response:
        """
        Create user, add to 'customer' group, log in via Django session, and return public profile.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()

        group, _ = Group.objects.get_or_create(name="customer")
        user.groups.add(group)

        # Session login so Swagger can use cookieAuth
        backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, user, backend=backend)

        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:
        """Return the public profile of the authenticated user."""
        return Response(UserPublicSerializer(request.user).data, status=status.HTTP_200_OK)
