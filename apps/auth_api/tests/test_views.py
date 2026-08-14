import json

import pytest
from django.contrib.auth.models import Group, User

from apps.auth_api.models import AuthToken


@pytest.mark.django_db
class TestLoginView:
    url = "/api/auth/login/"

    def _create_user(self) -> User:
        user = User.objects.create_user(username="alice", password="secret123")
        group, _ = Group.objects.get_or_create(name="analyst")
        user.groups.add(group)
        return user

    def test_login_success(self, client):
        self._create_user()
        response = client.post(
            self.url,
            data=json.dumps({"username": "alice", "password": "secret123"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["username"] == "alice"
        assert payload["roles"] == ["analyst"]
        assert len(payload["token"]) == 64

    def test_login_wrong_password(self, client):
        self._create_user()
        response = client.post(
            self.url,
            data=json.dumps({"username": "alice", "password": "wrong"}),
            content_type="application/json",
        )

        assert response.status_code == 401
        assert response.json() == {"success": False, "error": "Неверный логин или пароль"}

    def test_login_invalid_json(self, client):
        response = client.post(self.url, data="{not json", content_type="application/json")

        assert response.status_code == 400
        assert response.json() == {"success": False, "error": "Неверный формат JSON"}


@pytest.mark.django_db
class TestLogoutView:
    url = "/api/auth/logout/"

    def test_logout_with_valid_token(self, client, manager_user):
        token = AuthToken.create_token(manager_user, hours=24)
        response = client.post(self.url, HTTP_AUTHORIZATION=f"Token {token.token}")

        assert response.status_code == 200
        assert not AuthToken.objects.filter(token=token.token).exists()

    def test_logout_without_token(self, client):
        response = client.post(self.url)

        assert response.status_code == 400
        assert response.json() == {"success": False, "error": "Токен не предоставлен"}
