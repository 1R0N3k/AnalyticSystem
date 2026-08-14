import pytest
from django.http import JsonResponse
from django.test import RequestFactory
from django.views import View

from apps.auth_api.mixins import TokenRequiredMixin
from apps.auth_api.models import AuthToken


class _DummyView(TokenRequiredMixin, View):
    def get(self, request):
        return JsonResponse({"ok": True})


@pytest.mark.django_db
class TestTokenRequiredMixin:
    def test_401_without_token(self, client):
        response = client.get("/analytics/api/revenue/")

        assert response.status_code == 401
        assert "error" in response.json()

    def test_401_with_invalid_token(self, client):
        response = client.get("/analytics/api/revenue/", HTTP_AUTHORIZATION="Token deadbeef")

        assert response.status_code == 401

    def test_200_for_matching_role(self, client, analyst_user):
        token = AuthToken.create_token(analyst_user, hours=24)
        response = client.get("/analytics/api/revenue/", HTTP_AUTHORIZATION=f"Token {token.token}")

        assert response.status_code == 200

    def test_403_for_insufficient_role(self, client, analyst_user):
        token = AuthToken.create_token(analyst_user, hours=24)
        response = client.get("/analytics/api/margin/", HTTP_AUTHORIZATION=f"Token {token.token}")

        assert response.status_code == 403
        assert "manager" in response.json()["error"]

    def test_403_for_user_without_groups(self, client, plain_user):
        token = AuthToken.create_token(plain_user, hours=24)
        response = client.get("/analytics/api/revenue/", HTTP_AUTHORIZATION=f"Token {token.token}")

        assert response.status_code == 403

    def test_any_authenticated_user_passes_when_role_not_required(self, plain_user):
        token = AuthToken.create_token(plain_user, hours=24)
        request = RequestFactory().get("/", HTTP_AUTHORIZATION=f"Token {token.token}")

        response = _DummyView.as_view()(request)

        assert response.status_code == 200
