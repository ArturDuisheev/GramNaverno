from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Если не безопасный метод, то доступ разрешен только автору рецепта."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsAuthorOnly(permissions.BasePermission):
    """Доступ разрешен только автору рецепта."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
