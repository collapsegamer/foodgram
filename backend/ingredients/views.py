from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['^name']
    pagination_class = None
