import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.auth_api.models import AuthToken


@pytest.mark.django_db
class TestCreateToken:
    def test_creates_token_with_expected_format(self):
        user = User.objects.create_user(username="u1", password="pass")
        token_obj = AuthToken.create_token(user, hours=24)

        assert len(token_obj.token) == 64
        assert token_obj.user == user
        assert token_obj.expires_at > timezone.now()

    def test_replaces_previous_token_for_same_user(self):
        user = User.objects.create_user(username="u2", password="pass")
        first = AuthToken.create_token(user, hours=24)
        second = AuthToken.create_token(user, hours=24)

        assert first.token != second.token
        assert AuthToken.objects.filter(user=user).count() == 1


@pytest.mark.django_db
class TestValidateToken:
    def test_returns_user_for_valid_token(self):
        user = User.objects.create_user(username="u3", password="pass")
        token_obj = AuthToken.create_token(user, hours=24)

        assert AuthToken.validate_token(token_obj.token) == user

    def test_returns_none_and_deletes_expired_token(self):
        user = User.objects.create_user(username="u4", password="pass")
        token_obj = AuthToken.create_token(user, hours=-1)

        assert AuthToken.validate_token(token_obj.token) is None
        assert not AuthToken.objects.filter(token=token_obj.token).exists()

    def test_returns_none_for_unknown_token(self):
        assert AuthToken.validate_token("unknown-token") is None
