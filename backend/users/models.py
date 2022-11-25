from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER = 'user'
    ADMIN = 'admin'
    ROLES = [
        (USER, USER),
        (ADMIN, ADMIN)
    ]

    email = models.EmailField(max_length=255, unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    role = models.CharField(max_length=20, choices=ROLES, default=USER)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', ]
    USERNAME_FIELD = 'email'

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        ordering = ['username', 'email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribtion(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    class Meta:
        ordering = ['-user']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.author.username}'
