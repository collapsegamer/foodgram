from django.contrib import admin
from recipes.models import Recipe, IngredientAmount, Favorite


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorite_count')
    inlines = [IngredientAmountInline]
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')

    def favorite_count(self, obj):
        return obj.favorited_by.count()
    favorite_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
