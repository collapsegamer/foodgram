from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('email', unique=True, max_length=254)
    avatar = models.ImageField('avatar',
                               upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User, related_name='subscribers',
                               on_delete=models.CASCADE
                               )

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user.email} -> {self.author.email}'
