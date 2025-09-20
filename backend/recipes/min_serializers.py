from rest_framework import serializers
from .models import Recipe


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Минимальный сериализатор для отображения
       рецептов в избранном, корзине и подписках."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
