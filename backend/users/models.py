from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAXLENGTH_NAME, MAXLENGTH_EMAIL


class User(AbstractUser):
    """Модель для кастомного пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    first_name = models.CharField(
        max_length=MAXLENGTH_NAME, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAXLENGTH_NAME, verbose_name='Фамилия'
    )
    username = models.CharField(
        max_length=MAXLENGTH_NAME,
        unique=True,
        verbose_name='Никнейм',
    )
    email = models.EmailField(
        max_length=MAXLENGTH_EMAIL,
        unique=True,
        verbose_name='email',
    )
    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/images', verbose_name='Аватар'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'user'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель для подписчиков."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        default_related_name = 'subscriptions'
        ordering = ['user__username']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_user_following'
            ),
            models.CheckConstraint(
                name="prevent_self_following",
                check=~models.Q(following=models.F("user")),
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'
