from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()


class UserBaseSerializer(serializers.ModelSerializer):
    """Базовый пользователь: визитка для вложений и автора рецепта."""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class RecipeBaseSerializer(serializers.ModelSerializer):
    """Базовый рецепт: для избранного, корзины, вложенных списков."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
