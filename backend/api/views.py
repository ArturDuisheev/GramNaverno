from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework import filters
from rest_framework.response import Response

from recipes import models as rec_mod
from api import (
    serializers as api_ser,
    pagination as api_pag,
    permissions as api_per,
    filters as api_filter,
    utils as api_utils
)

User = get_user_model()


#      ******   РЕЦЕПТЫ   *******

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов рецепта. ReadOnly."""

    queryset = rec_mod.Ingredient.objects.all()
    serializer_class = api_ser.IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = api_filter.IngredientFilterSet


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов рецепта. ReadOnly."""

    queryset = rec_mod.Tag.objects.all()
    serializer_class = api_ser.TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = (api_per.IsAuthorOrReadOnly,)
    pagination_class = api_pag.RecipePagination
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = api_filter.RecipeTagsFilter

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = rec_mod.Recipe.objects.all()

        if self.action in ["list", "retrieve"]:
            queryset = (
                queryset.select_related('author')
                .prefetch_related('ingredients', 'tags')
                .order_by('-created_at')
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'get_link':
            return None
        elif self.action == 'shopping_cart':
            return api_ser.ShoppingCartSerializer
        elif self.action == "favorite":
            return api_ser.FavoriteRecipesSerializer
        elif self.action == 'list':
            return api_ser.RecipeFullSerializer
        return api_ser.RecipeCreateSerializer

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод для получения списка покупок."""
        user = self.request.user
        shopping_cart = api_utils.get_shopping_cart(user=user)

        with open("shopping_cart.txt", "w", encoding='utf-8') as file:
            file.writelines(shopping_cart)

        return FileResponse(
            open("shopping_cart.txt", "rb"),
            as_attachment=True,
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Метод для добавления/удаления рецепта из списка покупок."""
        try:
            recipe = rec_mod.Recipe.objects.get(pk=self.kwargs['pk'])

        except rec_mod.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = self.request.user

        if request.method == 'POST':
            try:
                serializer = self.get_serializer(
                    data={'recipe': recipe.pk},
                    context={'request': request},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        instance = rec_mod.UserShoppingCart.objects.filter(
            recipe=recipe, user=user
        ).all()
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, *args, **kwargs):
        """Метод для добавления/удаления рецепта из избранного."""
        try:
            recipe = rec_mod.Recipe.objects.get(pk=self.kwargs['pk'])

        except rec_mod.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = self.request.user
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'recipe': recipe.pk},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        instance = rec_mod.UserFavoriteRecipes.objects.filter(
            recipe=recipe, user=user).all()
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get', ],
        detail=True,
        url_path='get-link',
        url_name='get_link',
        permission_classes=[permissions.AllowAny, ],
    )
    def get_link(self, request, *args, **kwargs):
        """Метод для получения короткой ссылки на рецепт."""
        try:
            recipe = rec_mod.Recipe.objects.get(pk=self.kwargs['pk'])
        except rec_mod.Recipe.DoesNotExist:
            return Response({'detail': 'Recipe not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)

        host_url = self.request.get_host()
        instance = rec_mod.ShortLink.objects.filter(recipe=recipe)

        if not instance.exists():
            short_link = api_utils.get_short_link(host=host_url)
            return Response(
                {'short-link': short_link}, status=status.HTTP_200_OK
            )

        instance = rec_mod.ShortLink.objects.filter(recipe=recipe)[0]
        short_link = instance.short_url
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
