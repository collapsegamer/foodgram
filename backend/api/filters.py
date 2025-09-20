from rest_framework.filters import SearchFilter


class IngredientNameStartswithFilter(SearchFilter):
    search_param = 'name'
