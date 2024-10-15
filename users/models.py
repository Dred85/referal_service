from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = None
    phone = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="Номер телефона",
        help_text="Укажите номер телефона",
    )
    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Укажите email", **NULLABLE
    )
    avatar = models.ImageField(upload_to="users/", verbose_name="аватар", **NULLABLE)
    country = models.CharField(max_length=50, verbose_name="страна", **NULLABLE)

    invite_code = models.CharField(
        max_length=6,
        verbose_name="Инвайт-код",
        help_text="Автоматически генерируется при регистрации",
    )
    invited_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="referrals",
        verbose_name="Кем приглашён",
        help_text="Пользователь, который Вас пригласил",
        **NULLABLE
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.phone
