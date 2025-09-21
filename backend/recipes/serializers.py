from django.db import transaction
from rest_framework import serializers

from common.fields import Base64ImageField
from ingredients.models import Ingredient
from users.serializers import UserBaseSerializer
from .models import Recipe, RecipeIngredient, Favorite, ShoppingCart
from tags.serializers import TagSerializer


class RecipeBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор рецепта (минимальный набор полей)."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeMinifiedSerializer(RecipeBaseSerializer):
    """Минифицированный сериализатор (наследуется от базового)."""
    class Meta(RecipeBaseSerializer.Meta):
        fields = RecipeBaseSerializer.Meta.fields


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserBaseSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe=obj).exists()


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    ingredient = serializers.IntegerField(required=False)
    amount = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if 'id' not in data and 'ingredient' in data:
            data['id'] = data['ingredient']
        if 'id' not in data:
            raise serializers.ValidationError('Ингредиент не выбран.')
        return data


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        read_only_fields = ('id',)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Обязательное поле.')
        seen = set()
        for item in value:
            ingredient_id = item.get('id') or item.get('ingredient')
            if not ingredient_id:
                raise serializers.ValidationError('Ингредиент не выбран.')
            if ingredient_id in seen:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны.')
            seen.add(ingredient_id)
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient_id} не найден.')
        return value

    @transaction.atomic
    def _set_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item.get('id') or item.get('ingredient'),
                amount=item['amount'],
            ) for item in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag_ids = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe.tags.set(tag_ids)
        self._set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tag_ids = validated_data.pop('tags', None)
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        if ingredients is not None:
            self._set_ingredients(instance, ingredients)
        return super().update(instance, validated_data)
