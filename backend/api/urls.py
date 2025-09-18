from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    UserViewSet, SubscriptionViewSet, SubscriptionsListView,
    TagViewSet, IngredientViewSet, RecipeViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscriptionViewSet, basename='subscribe')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/',
         SubscriptionsListView.as_view(), name='subscriptions'),
]
