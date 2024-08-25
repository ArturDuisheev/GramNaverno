from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import INGREDIENT_MAXLENGTH, RECIPE_MAXLENGTH, UNIT_MAXLENGTH

User = get_user_model()


class MeasurementUnit(models.Model):
    """Модель для единиц измерения."""

    full_name = models.CharField(
        _('Единица измерения'),
        max_length=UNIT_MAXLENGTH
    )
    short_name = models.CharField(
        _('Ед.изм.(сокр.)'), max_length=UNIT_MAXLENGTH
    )

    class Meta:
        verbose_name = _('Единица измерения')
        verbose_name_plural = _('Единицы измерения')
        default_related_name = 'measurement_units'

    def __str__(self):
        return self.short_name


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        _('Название ингредиента'),
        max_length=INGREDIENT_MAXLENGTH
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        verbose_name=_('Единица измерения'),
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        default_related_name = 'ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        _('Название тега'),
        unique=True,
        max_length=RECIPE_MAXLENGTH
    )
    slug = models.SlugField(
        _('Слаг тега'),
        unique=True
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class ShortLink(models.Model):
    """Модель для хранения коротких ссылок."""

    recipe = models.OneToOneField(
        "Recipe",
        on_delete=models.CASCADE,
        unique=True
    )

    full_url = models.URLField(unique=True)
    short_url = models.URLField(
        unique=True, db_index=True, blank=True
    )

    class Meta:
        ordering = ('full_url',)
        constraints = [
            models.UniqueConstraint(
                fields=['full_url', 'short_url'],
                name='unique_fullurl_shorturl'
            ),
        ]

    def __str__(self) -> str:
        return self.short_url


class Recipe(models.Model):
    """Модель для рецепта."""

    name = models.CharField(
        _('Название рецепта'),
        max_length=RECIPE_MAXLENGTH
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор рецепта'),
        related_name='recipes'
    )
    text = models.TextField(_('Текст рецепта'))
    image = models.ImageField(
        _('Изображение готового блюда'), upload_to='recipes/images'
    )
    ingredients = models.ManyToManyField(
        Ingredient, _('Ингредиенты'), through='RecipeIngredient'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Время приготовления')
    )
    tags = models.ManyToManyField(
        Tag, _('Теги'),
        through='RecipeTags'
    )
    is_favorited = models.ManyToManyField(
        User, through='UserFavoriteRecipes',
        default=False,
        verbose_name=_('В избранное'),
        related_name='recipe_is_favorited'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        verbose_name=_('Список покупок'),
        through='UserShoppingCart',
        related_name='recipes_is_in_shhopping_cart',
    )
    created_at = models.DateTimeField(
        _('Дата публикации'),
        auto_now_add=True
    )
    short_link = models.OneToOneField(
        ShortLink,
        on_delete=models.CASCADE,
        verbose_name=_('Короткая ссылка'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


#                      *** ПРОМЕЖУТОЧНЫЕ МОДЕЛИ ***


class UserFavoriteRecipes(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        ordering = ('user',)
        default_related_name = 'user_favorite_recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_recipe'
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} - в Избранном у {self.user.name}.'


class UserShoppingCart(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')
        ordering = ('user',)
        default_related_name = 'user_shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_shopping_cart'
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} - в Списке покупок у {self.user.name}.'


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи Recipes/Ingredients."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredients'
            ),
        ]


class RecipeTags(models.Model):
    """Промежуточная модель для связи Recipes/Tags."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'recipe_tags'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe_id', 'tag_id'],
                name='unique_recipe_tag',
            ),
        ]
