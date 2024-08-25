from djoser import views as djoser_views
from djoser.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from api.serializers import (SubscribeSerializer, SubscriptionsSeriealizer)
from users.serializers import AvatarSerializer
from api.pagination import UserListPagination
from .permissions import SelfUserPermission

from users.models import Subscriptions


User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """
    Вьюсет для работы с пользователями.

    Наследуется от встроенного djoser_views.UserViewSet.
    """

    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_fields = 'email'
    pagination_class = UserListPagination

    def get_queryset(self):
        if self.action == "me":
            return User.objects.filter(pk=self.request.user.pk)
        if self.action == "subscriptions":
            return Subscriptions.objects.all()
        return User.objects.order_by('id').all()

    def get_serializer_class(self):
        action_serializer_map = {
            "create": settings.SERIALIZERS.user_create_password_retype
            if settings.USER_CREATE_PASSWORD_RETYPE else settings.SERIALIZERS.user_create,
            "set_password": settings.SERIALIZERS.set_password_retype
            if settings.SET_PASSWORD_RETYPE else settings.SERIALIZERS.set_password,
            "me": settings.SERIALIZERS.user if self.request.method == "GET"
            else settings.SERIALIZERS.current_user,
            "avatar": AvatarSerializer,
            "subscriptions": SubscriptionsSeriealizer,
            "subscribe": SubscribeSerializer
        }
        return action_serializer_map.get(self.action, self.serializer_class)

    @action(
        ["get"],
        detail=False,
        url_name='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        url_name='me_avatar',
        permission_classes=[SelfUserPermission],
    )
    def avatar(self, request, *args, **kwargs):
        """Метод для добавления/удаления своего аватара."""
        instance = User.objects.get(id=request.user.id)
        data = request.data
        if request.method == 'PUT':
            avatar = data.get('avatar')
            if not avatar:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(instance, data=data)
            serializer.is_valid()
            instance.avatar = serializer.validated_data.get(
                'avatar', instance.avatar
            )
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        """Метод для получения списка собственных подписок."""
        user = request.user
        queryset = Subscriptions.objects.all().filter(user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if not queryset.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        ['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id, *args, **kwargs):
        """Метод, чтобы подписаться/отписаться на другого пользователя."""
        user = get_object_or_404(User, id=self.request.user.id)
        following = get_object_or_404(User, id=self.kwargs['id'])

        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'following': following},
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
        user = get_object_or_404(User, id=self.request.user.id)
        following = get_object_or_404(User, id=self.kwargs['id'])
        instance = Subscriptions.objects.filter(
            following=following, user=user
        ).all()
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)