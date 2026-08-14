from django.http import JsonResponse

from .models import AuthToken

ROLE_LEVELS = {
    "analyst": 1,
    "manager": 2,
}


class TokenRequiredMixin:
    required_role: str | None = None

    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Token "):
            return JsonResponse({"success": False, "error": "Требуется авторизация (отсутствует токен)"}, status=401)

        token_key = auth_header.split(" ")[1]

        user = AuthToken.validate_token(token_key)

        if user is None:
            return JsonResponse({"success": False, "error": "Неверный или истёкший токен"}, status=401)

        if self.required_role:
            user_roles = set(user.groups.values_list("name", flat=True))
            required_level = ROLE_LEVELS.get(self.required_role, 99)
            user_max_level = max((ROLE_LEVELS.get(role, 0) for role in user_roles), default=0)

            if user_max_level < required_level:
                return JsonResponse(
                    {"success": False, "error": f"Доступ запрещён. Требуется роль: {self.required_role}"}, status=403
                )

        request.user = user
        return super().dispatch(request, *args, **kwargs)
