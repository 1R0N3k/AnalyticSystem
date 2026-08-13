import secrets

import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class AuthToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auth_tokens',
        verbose_name='Пользователь'
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Токен авторизации'
        verbose_name_plural = 'Токены авторизации'
        ordering = ['-created_at']

    def __str__(self):
        return f"Токен {self.user.username} (до {self.expires_at.strftime('%d.%m.%Y %H:%M')})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @classmethod
    def create_token(cls, user: User, hours: int = 24) -> AuthToken:
        token = secrets.token_hex(32)

        expires_at = timezone.now() + timezone.timedelta(hours=hours)
        cls.objects.filter(user=user).delete()

        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    @classmethod
    def validate_token(cls, token: str) -> User | None:
        try:
            auth_token = cls.objects.get(token=token)

            if auth_token.is_expired:
                auth_token.delete()
                return None

            return auth_token.user

        except cls.DoesNotExist:
            return None
