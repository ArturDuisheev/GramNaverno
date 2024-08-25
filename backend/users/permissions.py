from rest_framework import permissions


class SelfUserPermission(permissions.BasePermission):
    """Разрешение для просмотра и изменения собственных данных."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_admin


class AdminOrSuperUserOrReadOnly(permissions.BasePermission):
    """Ограничение доступа.

    Доступ только для админа или сюперюзера,
    либо только безопасные запросы.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_admin or request.user.is_superuser