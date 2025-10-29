# apps/reviews/serializers.py
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Review payload.

    Правила:
    - `author` проставляется автоматически (из request.user) и изменять нельзя.
    - `listing` указывать можно только при создании; через update менять нельзя.
    - `review_id` — алиас `id` в ответах для удобства в Swagger/UI.
    """
    review_id = serializers.IntegerField(source='id', read_only=True, help_text='Alias of `id` (Review ID)')

    class Meta:
        model = Review
        fields = '__all__'  # включает модельные поля; объявленный вручную review_id добавится сверху
        read_only_fields = ('author', 'created_at', 'updated_at')
        extra_kwargs = {
            'listing': {'help_text': 'Listing ID being reviewed'},
            'rating': {'help_text': 'Integer from 1 to 5'},
            'comment': {'help_text': 'Optional text comment', 'required': False},
        }

    def validate_rating(self, value):
        if value is None or not 1 <= int(value) <= 5:
            raise serializers.ValidationError('rating must be between 1 and 5')
        return value

    def update(self, instance, validated_data):
        # не позволяем менять автора и listing через PATCH/PUT
        validated_data.pop('author', None)
        validated_data.pop('listing', None)
        return super().update(instance, validated_data)
