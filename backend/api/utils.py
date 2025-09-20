from collections import defaultdict


def aggregate_ingredients(recipes):
    aggregate = defaultdict(int)
    for recipe in recipes.prefetch_related('recipe_ingredients__ingredient'):
        for ri in recipe.recipe_ingredients.all():
            key = (ri.ingredient.name, ri.ingredient.measurement_unit)
            aggregate[key] += ri.amount
    return aggregate
