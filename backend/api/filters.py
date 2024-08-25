from django_filters import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilterSet(FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeTagsFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )
    is_favorited = filters.NumberFilter(
        method='is_favorited_filter'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user.id
        if value == 1:
            queryset = Recipe.objects.all()
            return queryset.filter(is_in_shopping_cart__id=user)
        return queryset

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user.id
        if value == 1:
            queryset = Recipe.objects.all()
            return queryset.filter(is_favorited__id=user)
        return queryset
