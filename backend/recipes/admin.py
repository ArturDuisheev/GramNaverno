from django.contrib import admin

from .constants import LIST_PAGE
from .models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    RecipeTags,
    Tag,
    UserFavoriteRecipes,
)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagsInline(admin.TabularInline):
    model = RecipeTags
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    empty_value_display = 'тут пусто'
    list_per_page = LIST_PAGE
    list_filter = ('name',)
    search_fields = ('name',)
    inlines = (RecipeIngredientsInline,)


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'short_name')
    empty_value_display = 'тут пусто'
    list_filter = ('full_name', 'short_name')
    search_fields = ('full_name', 'short_name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    empty_value_display = 'тут пусто'
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')
    inlines = (RecipeTagsInline,)


class UserFavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    empty_value_display = 'тут пусто'
    list_filter = ('recipe', 'user')
    search_fields = ('recipe', 'user')


class UserFavoriteRecipesInline(admin.TabularInline):
    model = UserFavoriteRecipes
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'is_favorite',
    )
    empty_value_display = 'тут пусто'

    list_filter = ('tags',)
    search_fields = (
        'name',
        'author',
        'tags',
    )
    inlines = (
        RecipeIngredientsInline,
        RecipeTagsInline,
        UserFavoriteRecipesInline,
    )

    def is_favorite(self, obj=Recipe):
        return UserFavoriteRecipes.objects.filter(recipe=obj.id).count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(UserFavoriteRecipes, UserFavoriteRecipesAdmin)
