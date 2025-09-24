from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.utils import aggregate_ingredients
from shortener.models import ShortLink
from shortener.utils import generate_code
from .models import Recipe, Favorite, ShoppingCart, RecipeIngredient
from .serializers import (
    RecipeListSerializer, RecipeCreateUpdateSerializer
)
from .filters import RecipeFilter
from common.serializers import RecipeBaseSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        'tags',
        Prefetch('recipe_ingredients',
                 queryset=RecipeIngredient.objects.select_related('ingredient')
                 ),
    ).select_related('author')
    pagination_class = LimitPageNumberPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateUpdateSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        read_serializer = RecipeListSerializer(
            recipe, context={'request': request})
        return Response(read_serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = RecipeCreateUpdateSerializer(
            instance, data=request.data,
            partial=partial, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        read_serializer = RecipeListSerializer(
            recipe, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = ShortLink.objects.filter(
            target_path=f'/recipes/{recipe.id}/').first()
        if not link:
            code = generate_code(3)
            link = ShortLink.objects.create(
                code=code, target_path=f'/recipes/{recipe.id}/')
        base = request.build_absolute_uri('/')[:-1]
        return Response({'short-link': f'{base}/s/{link.code}'},
                        status=status.HTTP_200_OK
                        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated]
            )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            obj, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({'detail': 'Рецепт уже в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            return Response(
                RecipeBaseSerializer(recipe,
                                     context={'request': request}
                                     ).data,
                status=status.HTTP_201_CREATED)
        deleted, _ = Favorite.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            return Response({'detail': 'Рецепта не было в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated]
            )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({'detail': 'Рецепт уже в списке покупок.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                RecipeBaseSerializer(
                    recipe,
                    context={'request': request}).data,
                status=status.HTTP_201_CREATED)

        deleted, _ = ShoppingCart.objects.filter(
            user=user, recipe=recipe).delete()
        if not deleted:
            return Response({'detail': 'Рецепта не было в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated]
            )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(in_carts__user=request.user)
        agg = aggregate_ingredients(recipes)
        lines = []
        for (name, unit), amount in agg.items():
            lines.append(f'{name} — {amount} {unit}')
        content = '\n'.join(lines) if lines else 'Список покупок пуст.'
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response
