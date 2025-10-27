from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class UserPublicSerializer(UserSerializer):
    pass


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "username")

    def validate_email(self, value):
        value = (value or "").strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()
        password = validated_data["password"]
        base = (validated_data.get("username") or email.split("@")[0]).strip().lower() or "user"

        username = base
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"
            i += 1

        return User.objects.create_user(username=username, email=email, password=password)
