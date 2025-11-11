# apps/listings/serializers.py
from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    """
    Listing payload.

    Notes:
    - `owner` не редактируется через API (ставится на create из request.user).
    - `listing_id` — удобный alias к `id`, чтобы в UI не путаться.
    """
    # явный alias, чтобы в ответах было и id, и listing_id
    listing_id = serializers.IntegerField(
        source='id',
        read_only=True,
        help_text='Alias of `id` (Listing ID)'
    )

    class Meta:
        model = Listing
        # __all__ подтянет все модельные поля (включая id), а listing_id добавляем явно
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
        extra_kwargs = {
            'title': {'help_text': 'Short title'},
            'description': {'help_text': 'Long description'},
            'city': {'help_text': 'City'},
            'district': {'help_text': 'District'},
            'price': {'help_text': 'Price per period'},
            'rooms': {'help_text': 'Number of rooms'},
            'listing_type': {'help_text': 'Listing type (choices)'},
            'is_active': {'help_text': 'Visible in catalog'},
        }

    # простые проверки на уровне сериализатора
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Price must be ≥ 0')
        return value

    def validate_rooms(self, value):
        if value is not None and not (1 <= value <= 20):
            raise serializers.ValidationError('Rooms must be between 1 and 20')
        return value

    def update(self, instance, validated_data):
        # не даём менять владельца через PATCH/PUT
        validated_data.pop('owner', None)
        return super().update(instance, validated_data)
