from rest_framework import serializers
from django.contrib.auth import get_user_model
from common.fields import Base64ImageField
from recipes.models import Recipe
from recipes.serializers import RecipeMinifiedSerializer
from .models import Subscription

User = get_user_model()


class UserBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя (минимальный набор полей)."""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserMinifiedSerializer(UserBaseSerializer):
    """Минифицированный сериализатор (наследуется от базового)."""
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields


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
        return Subscription.objects.filter(user=request.user,
                                           author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'avatar',
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        qs = Recipe.objects.filter(author=obj)
        if limit:
            qs = qs[:int(limit)]
        return RecipeMinifiedSerializer(qs, many=True,
                                        context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class SetAvatarResponseSerializer(serializers.Serializer):
    avatar = serializers.ImageField()
