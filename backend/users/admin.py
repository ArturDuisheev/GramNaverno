from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import Subscriptions
from recipes.models import UserFavoriteRecipes, UserShoppingCart

User = get_user_model()


class UserFavoriteRecipesInline(admin.TabularInline):
    model = UserFavoriteRecipes
    extra = 1


class UserShoppingCartInline(admin.TabularInline):
    model = UserShoppingCart
    extra = 1


@admin.register(User)
class UsertAdmin(BaseUserAdmin):

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
    )
    empty_value_display = 'тут пусто'
    list_filter = ('username', 'email', 'first_name')
    search_fields = ('username', 'email', 'first_name')
    inlines = (UserFavoriteRecipesInline, UserShoppingCartInline)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following'
    )
    empty_value_display = 'тут пусто'
    list_filter = ('user__username',)
    search_fields = ('user__username',)


admin.site.unregister(Group)
