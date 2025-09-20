from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipeViewSet
from ingredients.views import IngredientViewSet
from tags.views import TagViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
