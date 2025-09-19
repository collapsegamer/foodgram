from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    UserSerializer, UserCreateSerializer, SetAvatarSerializer,
    TagSerializer, IngredientSerializer,
    RecipeListSerializer, RecipeCreateUpdateSerializer
)
from django.contrib.auth import get_user_model
from tags.models import Tag
from ingredients.models import Ingredient
from recipes.models import Recipe, Favorite, ShoppingCart
from recipes.models import Subscription

User = get_user_model()


# Users
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='set-avatar'
    )
    def set_avatar(self, request):
        serializer = SetAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.avatar = serializer.validated_data['avatar']
        user.save()
        return Response({'avatar': user.avatar.url},
                        status=status.HTTP_200_OK)

    @set_avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.DestroyModelMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, user_id=None):
        author = get_object_or_404(User, pk=user_id)
        if author == request.user:
            return Response({'detail': 'Нельзя подписаться на себя'},
                            status=400)
        Subscription.objects.create(user=request.user, author=author)
        return Response(
            UserSerializer(author, context=self.get_serializer_context()).data,
            status=201
        )

    def destroy(self, request, user_id=None):
        sub = Subscription.objects.filter(user=request.user, author_id=user_id)
        if not sub.exists():
            return Response(status=400)
        sub.delete()
        return Response(status=204)


class SubscriptionsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(subscribers__user=self.request.user)


# Tags
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


# Ingredients
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


# Recipes
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.all().prefetch_related('tags', 'ingredient_amounts')
    )
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'author__username', 'tags__slug']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        return Response(status=201)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        Favorite.objects.filter(user=request.user, recipe_id=pk).delete()
        return Response(status=204)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
        return Response(status=201)

    @shopping_cart.mapping.delete
    def remove_from_cart(self, request, pk=None):
        ShoppingCart.objects.filter(user=request.user, recipe_id=pk).delete()
        return Response(status=204)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        items = ShoppingCart.objects.filter(user=request.user)
        agg = {}
        for cart in items:
            for ia in cart.recipe.ingredient_amounts.all():
                key = (ia.ingredient.name, ia.ingredient.measurement_unit)
                agg[key] = agg.get(key, 0) + ia.amount
        lines = [f'{n} ({u}) — {a}' for (n, u), a in agg.items()]
        return Response('\n'.join(lines), content_type='text/plain')
