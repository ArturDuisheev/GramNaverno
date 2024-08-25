from djoser import serializers as djoser_serializers
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator, RegexValidator
from rest_framework import serializers

from users.constants import MAXLENGTH_NAME, MAXLENGTH_EMAIL


User = get_user_model()


class UserSignupSerializer(djoser_serializers.UserCreateSerializer):

    email = serializers.EmailField(
        allow_blank=False,
        max_length=MAXLENGTH_EMAIL,
        required=True,
        validators=[
            EmailValidator(
                message='Введите корректный email',
            ),
        ],
    )

    username = serializers.CharField(
        max_length=MAXLENGTH_NAME,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Введите корректный Username.',
            )
        ],
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер для изменения/удаления своего аватара."""

    avatar = serializers.ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
