from django.db.models import Sum
from recipes.models import RecipeIngredient


def aggregate_ingredients(recipes):
    """
    Принимает queryset рецептов или список объектов Recipe.
    Возвращает словарь { (ingredient_name, measurement_unit): total_amount }.
    """
    # Получаем список id рецептов
    recipe_ids = (
        recipes.values_list('id', flat=True)
        if hasattr(recipes, 'values_list')
        else [r.id for r in recipes]
    )

    qs = (
        RecipeIngredient.objects
        .filter(recipe_id__in=recipe_ids)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_amount=Sum('amount'))
    )

    return {
        (row['ingredient__name'],
         row['ingredient__measurement_unit']): row['total_amount']
        for row in qs
    }

# from collections import defaultdict
#
#
# def aggregate_ingredients(recipes):
#     aggregate = defaultdict(int)
#     for recipe in recipes.prefetch_related('recipe_ingredients__ingredient'):
#         for ri in recipe.recipe_ingredients.all():
#             key = (ri.ingredient.name, ri.ingredient.measurement_unit)
#             aggregate[key] += ri.amount
#     return aggregate
