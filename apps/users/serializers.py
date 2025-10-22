from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration payload.
    Password is write-only; username/email must be unique.
    """
    password = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )


class UserPublicSerializer(serializers.ModelSerializer):
    """Public user profile."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
