from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount,
                     Recipe, ShoppingCart, Tag)

class RecipeAdmin(admin.ModelAdmin):
    fields = [
        'tags', 'author', 'ingredients', 'name', 'image', 'text',
        'cooking_time', 'pub_date', 'recipe_favorited_count'
    ]
    readonly_fields = ('pub_date', 'recipe_favorited_count')

    def get_recipe_favorited_count(self, obj):
        return obj.recipe_favorited_count()


admin.site.register(Favorite)
admin.site.register(Ingredient)
admin.site.register(IngredientAmount)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
