from django.contrib import admin
from django.utils.html import format_html

from .models import AuthToken

# Register your models here.


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_expired_status')
    list_filter = ('user', 'expires_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'expires_at')

    def token(self, obj):
        return f"{obj.token[:8]}...{obj.token[-8:]}"

    def is_expired_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Истёк</span>')
        return format_html('<span style="color: green;">Активен</span>')
    is_expired_status.short_description = 'Статус'
