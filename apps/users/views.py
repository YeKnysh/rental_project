from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .serializers import RegisterSerializer, UserPublicSerializer

User = get_user_model()


@extend_schema_view(
    register=extend_schema(
        tags=["users"],
        summary="Register a new user",
        request=RegisterSerializer,
        responses={201: OpenApiResponse(response=UserPublicSerializer, description="Created")},
    ),
    me=extend_schema(
        tags=["users"],
        summary="Get current user profile",
        responses={200: UserPublicSerializer},
    ),
)
class UsersViewSet(viewsets.ViewSet):
    """
    Users API.
    - POST /users/register/ — create a new user (default to 'customer' group)
    - GET  /users/me/       — current user profile (auth required)
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        grp = Group.objects.filter(name='customer').first()
        if grp:
            user.groups.add(grp)

        data = UserPublicSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response(UserPublicSerializer(request.user).data)
