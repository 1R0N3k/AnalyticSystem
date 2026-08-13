from django.http import JsonResponse

from .models import AuthToken


class TokenRequiredMixin:
    required_role = None
    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Token '):
            return JsonResponse(
                {'success': False, 'error': 'Требуется авторизация (отсутствует токен)'},
                status=401
            )

        token_key = auth_header.split(' ')[1]

        user = AuthToken.validate_token(token_key)

        if user is None:
            return JsonResponse(
                {'success': False, 'error': 'Неверный или истёкший токен'},
                status=401
            )

        if self.required_role:
            user_roles = user.groups.values_list('name', flat=True)
            if self.required_role not in user_roles:
                return JsonResponse(
                    {'success': False, 'error': f'Доступ запрещён. Требуется роль: {self.required_role}'},
                    status=403
                )

        request.user = user
        return super().dispatch(request, *args, **kwargs)
