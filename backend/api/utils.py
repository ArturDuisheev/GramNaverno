import random

from rest_framework import status
from rest_framework.response import Response

from recipes.constants import CHARACTERS, SHORT_URL_LENGTH
from recipes.models import ShortLink, RecipeIngredient, UserShoppingCart


def get_short_link(host):
    """Генерирует уникальную короткую ссылку для рецепта."""
    while True:
        short_url = f'https://{host}/s/' + ''.join(
            random.choices(CHARACTERS, k=SHORT_URL_LENGTH)
        ) + '/'
        if not ShortLink.objects.filter(short_url=short_url).exists():
            return short_url


def get_shopping_cart(user):
    """Получает список покупок пользователя."""
    recipes = UserShoppingCart.objects.filter(user=user).select_related('recipe')

    if not recipes.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    shopping_list = {}

    for user_recipe in recipes:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=user_recipe.recipe).select_related('ingredient')

        for item in recipe_ingredients:
            ingredient_name = item.ingredient.name
            measurement_unit = item.ingredient.measurement_unit.short_name
            ingredient_key = f'{ingredient_name} ({measurement_unit})'

            if ingredient_key in shopping_list:
                shopping_list[ingredient_key] += item.amount
            else:
                shopping_list[ingredient_key] = item.amount

    shopping_cart = [
        f'{ingredient} - {amount}\n' for ingredient, amount in shopping_list.items()
    ]

    return shopping_cart
