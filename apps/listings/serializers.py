from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    """
    Listing payload.

    Notes:
    - `owner` is read-only; it is set from the request user on create.
    """

    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
        extra_kwargs = {
            'title': {'help_text': 'Short title'},
            'description': {'help_text': 'Long description'},
            'city': {'help_text': 'City'},
            'district': {'help_text': 'District'},
            'price': {'help_text': 'Price per period'},
            'rooms': {'help_text': 'Number of rooms'},
            'type': {'help_text': 'Listing type (choices)'},
            'is_active': {'help_text': 'Visible in catalog'},
        }

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Price must be ≥ 0')
        return value

    def validate_rooms(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Rooms must be ≥ 0')
        return value

    def update(self, instance, validated_data):
        validated_data.pop('owner', None)  # не даём менять владельца через сериализатор
        return super().update(instance, validated_data)
