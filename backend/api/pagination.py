from rest_framework.pagination import LimitOffsetPagination


class RecipePagination(LimitOffsetPagination):
    default_limit = 6
    max_limit = 6
    min_limit = 2


class SubscriptionPagination(LimitOffsetPagination):
    limit_query_param = 'limit'
    default_limit = 2
    max_limit = 2
    min_limit = 1


class AuthorRecipesPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
    default_limit = 11
    max_limit = 11
    min_limit = 2


class UserListPagination(LimitOffsetPagination):
    default_limit = 4
    max_limit = 4
    min_limit = 1
