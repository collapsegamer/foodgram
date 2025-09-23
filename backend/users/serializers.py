from rest_framework import serializers
from django.contrib.auth import get_user_model
from common.fields import Base64ImageField
from common.serializers import UserBaseSerializer, RecipeBaseSerializer
from .models import Subscription
from recipes.models import Recipe, ShoppingCart

User = get_user_model()


class UserSerializer(UserBaseSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta(UserBaseSerializer.Meta):
        model = User
        fields = (*UserBaseSerializer.Meta.fields, 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )
        return user


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'recipes', 'recipes_count',
                  'cart_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        qs = Recipe.objects.filter(author=obj)
        if limit:
            try:
                limit_value = int(limit)
                if limit_value > 0:
                    qs = qs[:limit_value]
            except (ValueError, TypeError):
                pass

        return RecipeBaseSerializer(qs, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_cart_count(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return 0
        return ShoppingCart.objects.filter(user=user).count()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class SetAvatarResponseSerializer(serializers.Serializer):
    avatar = serializers.ImageField()
