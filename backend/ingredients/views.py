from rest_framework import viewsets, mixins
from api.filters import IngredientNameStartswithFilter
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientNameStartswithFilter]
    search_fields = ['^name']
    pagination_class = None
