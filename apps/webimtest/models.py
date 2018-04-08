from django.db import models
from django.contrib.auth.models import User, UserManager


class UserVK(User):
    """
        Аккаунт пользователя
    """

    class Meta:
        db_table = "uservk"
        verbose_name = "Аккаунт пользователя"
        verbose_name_plural = "Аккаунты пользователей"

    token = models.CharField(verbose_name="Токен", max_length=200)

    def __str__(self):
        return self.username

    objects = UserManager()
