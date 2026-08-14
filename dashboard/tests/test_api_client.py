import pytest
import requests

from dashboard.services import api_client


class FakeResponse:
    def __init__(self, status_code: int = 200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code} error")


class TestLoginUser:
    def test_success_sets_session_state(self, monkeypatch):
        payload = {"token": "tok123", "username": "alice", "roles": ["analyst"]}

        def fake_post(url, json=None):
            assert url == f"{api_client.AUTH_API_BASE_URL}/login/"
            assert json == {"username": "alice", "password": "secret"}
            return FakeResponse(200, payload)

        monkeypatch.setattr(api_client.requests, "post", fake_post)

        assert api_client.login_user("alice", "secret") is True
        assert api_client.st.session_state.auth_token == "tok123"
        assert api_client.st.session_state.username == "alice"
        assert api_client.st.session_state.roles == ["analyst"]

    def test_failure_returns_false(self, monkeypatch):
        monkeypatch.setattr(
            api_client.requests,
            "post",
            lambda *args, **kwargs: FakeResponse(401, {"error": "Неверный логин или пароль"}),
        )

        assert api_client.login_user("alice", "wrong") is False
        assert "auth_token" not in api_client.st.session_state


class TestLogoutUser:
    def test_calls_api_and_clears_session(self, monkeypatch):
        api_client.st.session_state.auth_token = "tok123"
        captured = {}

        def fake_post(url, headers=None):
            captured["headers"] = headers
            return FakeResponse(200)

        monkeypatch.setattr(api_client.requests, "post", fake_post)
        monkeypatch.setattr(api_client.st, "rerun", lambda: None)

        api_client.logout_user()

        assert captured["headers"] == {"Authorization": "Token tok123"}
        assert "auth_token" not in api_client.st.session_state


class TestGetRevenue:
    def test_passes_params_and_token_header(self, monkeypatch):
        api_client.st.session_state.auth_token = "tok123"
        expected = [{"day": "2026-01-10", "revenue": 100.0}]

        def fake_get(url, params=None, headers=None):
            assert url == f"{api_client.API_BASE_URL}/revenue/"
            assert params == {"start": "2026-01-01", "end": "2026-01-31"}
            assert headers == {"Authorization": "Token tok123"}
            return FakeResponse(200, expected)

        monkeypatch.setattr(api_client.requests, "get", fake_get)

        assert api_client.get_revenue("2026-01-01", "2026-01-31") == expected

    def test_raises_on_error_status(self, monkeypatch):
        monkeypatch.setattr(api_client.requests, "get", lambda *a, **kw: FakeResponse(500))

        with pytest.raises(requests.HTTPError):
            api_client.get_revenue()


@pytest.mark.parametrize(
    "method_name,empty_result",
    [
        ("get_margin", {}),
        ("get_margin_by_day", []),
        ("get_abc_analysis", []),
        ("get_revenue_by_day_of_week", []),
        ("get_revenue_by_hour", []),
        ("get_revenue_by_month", []),
        ("get_top_customers_data", []),
    ],
    ids=["margin", "margin-by-day", "abc", "day-of-week", "hour", "month", "top-customers"],
)
class TestManagerEndpoints:
    def test_401_signals_session_expired(self, monkeypatch, method_name, empty_result):
        api_client.st.session_state.auth_token = "tok123"
        logged_out = []

        monkeypatch.setattr(api_client.requests, "get", lambda *a, **kw: FakeResponse(401))
        monkeypatch.setattr(api_client, "logout_user", lambda: logged_out.append(True))

        result = getattr(api_client, method_name)()

        assert result == empty_result
        assert logged_out == [True]

    def test_403_returns_empty_result(self, monkeypatch, method_name, empty_result):
        monkeypatch.setattr(
            api_client.requests,
            "get",
            lambda *a, **kw: FakeResponse(403, {"error": "Доступ запрещён"}),
        )

        assert getattr(api_client, method_name)() == empty_result
