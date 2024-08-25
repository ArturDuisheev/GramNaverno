from djoser import serializers as djoser_serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .pagination import AuthorRecipesPagination
from recipes import models as recipes_models
from users.models import Subscriptions


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов."""

    measurement_unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = recipes_models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Скриализатор для тегов."""

    class Meta:
        model = recipes_models.Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id', 'name', 'slug')


class UserGetSerializer(djoser_serializers.UserSerializer):
    """
    Сериализатор для получения данных пользователей ('list', 'retirieve').

    Наследуется от встроенного UserSerializer. ReadOnly.
    """

    id = serializers.IntegerField()
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed', default=False
    )
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        ]

    def get_is_subscribed(self, obj):
        """
        Метод сериалайзера.

        Проверяет, подписан ли текущий пользователь на
        пользователя, профиль которого он смотрит.
        """
        request_user = self.context.get('request').user.id
        queryset = Subscriptions.objects.filter(
            following=obj.id, user=request_user
        ).exists()
        return queryset


#                 ****  РЕЦЕПТЫ   *****

class RecipeBaseMixin(serializers.ModelSerializer):
    """Сериалайзер-миксин для рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = recipes_models.Recipe
        fields = ('name', 'image', "cooking_time")
        abstract = True


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления/удаления рецептов в Избранное."""

    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        queryset=User.objects.all(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=recipes_models.Recipe.objects.all()
    )

    class Meta:
        model = recipes_models.UserFavoriteRecipes
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=recipes_models.UserFavoriteRecipes.objects.all(),
                fields=('user', 'recipe'),
                message="Этот рецепт уже находится в Избранном",
            ),
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe, context=self.context).data


class RecipeTagsSerializer(serializers.ModelSerializer):
    """Сериалайзер для промежуточной модели RecipeIngredient."""

    recipe = serializers.PrimaryKeyRelatedField(
        queryset=recipes_models.Recipe.objects.all(), write_only=True
    )
    tag = serializers.PrimaryKeyRelatedField(
        queryset=recipes_models.Tag.objects.all(), write_only=True
    )

    class Meta:
        model = recipes_models.RecipeTags
        fields = ('recipe', 'tag')
        validators = [
            UniqueTogetherValidator(
                queryset=recipes_models.RecipeIngredient.objects.all(),
                fields=('recipe', 'tag'),
            )
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для промежуточной модели RecipeIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=recipes_models.Ingredient.objects.all()
    )

    class Meta:
        model = recipes_models.RecipeIngredient
        fields = ('id', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для представления поля ingredients.

    (В REcipeFullSerializer).
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = recipes_models.RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(RecipeBaseMixin):
    """Сериализатор для создания и изменения рецептов."""

    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=recipes_models.Tag.objects.all(), required=True
    )
    text = serializers.CharField(required=True)

    class Meta:
        model = recipes_models.Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        recipe, created = recipes_models.Recipe.objects.get_or_create(
            author=self.context['request'].user, **validated_data
        )

        self._add_tags(recipe, tags_data)
        self._add_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data, *args, **kwargs):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        tags_data = validated_data.get('tags')
        ingredients_data = validated_data.get('recipe_ingredients')

        if tags_data is not None:
            instance.tags.clear()
            self._add_tags(instance, tags_data)

        if ingredients_data is not None:
            instance.ingredients.clear()
            self._add_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def _add_tags(self, recipe, tags_data):
        if not tags_data:
            raise serializers.ValidationError("Не указаны тэги")
        for tag in tags_data:
            if recipe.tags.filter(id=tag.id).exists():
                recipe.delete()
                raise serializers.ValidationError("Повторяющиеся тэги")
            recipe.tags.add(tag)

    def _add_ingredients(self, recipe, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError("Не указаны ингредиенты")
        for ingredient in ingredients_data:
            if recipe.ingredients.filter(id=ingredient['ingredient'].id).exists():
                recipe.delete()
                raise serializers.ValidationError("Повторяющиеся ингредиенты")
            recipe.ingredients.add(
                ingredient['ingredient'],
                through_defaults={'amount': ingredient['amount']},
            )

    def to_representation(self, instance):
        return RecipeFullSerializer(instance, context=self.context).data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Не указаны ингредиенты")
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Не указаны тэги")
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Пустое изображение")
        return value


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка покупок."""

    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username',
    )

    class Meta:
        model = recipes_models.UserShoppingCart
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context
        ).data


class RecipeShortSerializer(RecipeBaseMixin):
    """Сериалайзер для короткого списка рецептов (GET-запрос)."""

    image = Base64ImageField(required=False, allow_null=False)

    class Meta(RecipeBaseMixin.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', "cooking_time")


class RecipeFullSerializer(RecipeBaseMixin):
    """Cериализатор для полного представления рецепта."""

    tags = TagSerializer(many=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited', read_only=True, default=False
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True,
        default=False
    )
    text = serializers.CharField(required=True)

    class Meta:
        model = recipes_models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        return recipes_models.UserFavoriteRecipes.objects.filter(recipe=obj.id, user=request_user).exists()

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        return recipes_models.UserShoppingCart.objects.filter(
            recipe=obj.id, user=request_user
        ).exists()


class AuthorProfileSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для профиля пользователя.

    Представляет полный профиль другого пользователя(автора рецепта.)
    """

    id = serializers.IntegerField()
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed', default=False
    )
    recipes = serializers.SerializerMethodField('get_recipes', read_only=True)
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count',
        read_only=True,
    )
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Метод сериалайзера.

        Проверяет, подписан ли текущий пользователь на
        пользователя, профиль которого он смотрит.
        """
        request_user = self.context.get('request').user.id
        queryset = Subscriptions.objects.filter(
            following=obj.id, user=request_user
        ).exists()
        return queryset

    def get_recipes(self, obj):
        author = get_object_or_404(User, id=obj.id)
        queryset = author.recipes.order_by('-created_at').all()
        paginator = AuthorRecipesPagination()
        paginated_queryset = paginator.paginate_queryset(
            queryset, request=self.context.get('request')
        )
        serializer = RecipeShortSerializer(paginated_queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        author = get_object_or_404(User, id=obj.id)
        queryset = author.recipes.all()
        return queryset.count()


class SubscriptionsSeriealizer(serializers.ModelSerializer):
    """Сериализатор для списка собсьвенных подписок(GET)."""

    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='email',
    )
    following = serializers.SlugRelatedField(
        slug_field='username', read_only=True, many=True
    )

    class Meta:
        model = Subscriptions
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('user', 'following'),
                message="Вы уже подписаны на этого пользователя!",
            ),
        ]

    def validate_following(self, data):
        user = self.context['request'].user
        if data == user:
            raise serializers.ValidationError(
                'Пользователь не может быть подписан на самого себя!'
            )
        return data

    def to_representation(self, instance):
        return AuthorProfileSerializer(
            instance.following, context=self.context
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/удаления подписки (POST, DELETE)."""

    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username',
    )
    following = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    class Meta:
        model = Subscriptions
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('user', 'following'),
                message="Вы уже подписаны на этого пользователя!",
            ),
        ]

    def validate_following(self, data):
        user = self.context['request'].user
        if data == user:
            raise serializers.ValidationError(
                'Пользователь не может быть подписан на самого себя!'
            )
        return data

    def to_representation(self, instance):
        return AuthorProfileSerializer(
            instance.following, context=self.context
        ).data
