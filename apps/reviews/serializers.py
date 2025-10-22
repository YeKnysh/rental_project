from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Review payload.

    Notes:
    - `author` is read-only; it is set from the request user on create.
    """

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')
        extra_kwargs = {
            'listing': {'help_text': 'Listing ID being reviewed'},
            'rating': {'help_text': 'Integer from 1 to 5'},
            'comment': {'help_text': 'Optional text comment', 'required': False},
        }

    def validate_rating(self, value):
        if value is None or not 1 <= value <= 5:
            raise serializers.ValidationError('rating must be between 1 and 5')
        return value

    def update(self, instance, validated_data):
        # do not allow changing author via serializer
        validated_data.pop('author', None)
        return super().update(instance, validated_data)
