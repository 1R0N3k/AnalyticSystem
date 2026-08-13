import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import AuthToken

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                token_obj = AuthToken.create_token(user, hours=24)

                roles = list(user.groups.values_list('name', flat=True))

                return JsonResponse({
                    'success': True,
                    'token': token_obj.token,
                    'username': user.username,
                    'roles': roles
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный логин или пароль'
                }, status=401)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Неверный формат JSON'
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            AuthToken.objects.filter(token=token_key).delete()
            return JsonResponse({'success': True, 'message': 'Выход выполнен'}, status=200)

        return JsonResponse({'success': False, 'error': 'Токен не предоставлен'}, status=400)
