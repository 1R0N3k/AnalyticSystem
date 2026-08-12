from django.http import JsonResponse
from .models import AuthToken


class TokenRequiredMixin:
    """
    Mixin для защиты Class-Based Views.
    Проверяет токен в заголовке и роль пользователя перед выполнением запроса.
    """
    required_role = None  # Переопределяется в конкретном View

    def dispatch(self, request, *args, **kwargs):
        # 1. Получаем токен из заголовка
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Token '):
            return JsonResponse(
                {'success': False, 'error': 'Требуется авторизация (отсутствует токен)'}, 
                status=401
            )
        
        token_key = auth_header.split(' ')[1]
        
        # 2. Валидируем токен
        user = AuthToken.validate_token(token_key)
        
        if user is None:
            return JsonResponse(
                {'success': False, 'error': 'Неверный или истёкший токен'}, 
                status=401
            )
        
        # 3. Проверяем роль (если она указана для этого View)
        if self.required_role:
            user_roles = user.groups.values_list('name', flat=True)
            if self.required_role not in user_roles:
                return JsonResponse(
                    {'success': False, 'error': f'Доступ запрещён. Требуется роль: {self.required_role}'}, 
                    status=403
                )
        
        # 4. Всё ок, добавляем пользователя в request и передаём управление дальше
        request.user = user
        return super().dispatch(request, *args, **kwargs)