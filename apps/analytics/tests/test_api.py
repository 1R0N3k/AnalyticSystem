import pytest

ANALYST_ENDPOINTS = [
    "/analytics/api/revenue/",
    "/analytics/api/top-products/",
    "/analytics/api/average-check/",
    "/analytics/api/customers-by-city/",
    "/analytics/api/funnel/",
]

MANAGER_ENDPOINTS = [
    "/analytics/api/margin/",
    "/analytics/api/margin-by-day/",
    "/analytics/api/abc-analysis/",
    "/analytics/api/revenue-by-day-of-week/",
    "/analytics/api/revenue-by-hour/",
    "/analytics/api/revenue-by-months/",
    "/analytics/api/top-customers/",
]

ALL_ENDPOINTS = ANALYST_ENDPOINTS + MANAGER_ENDPOINTS

DATE_ENDPOINTS = [
    ("/analytics/api/revenue/", "analyst_headers"),
    ("/analytics/api/average-check/", "analyst_headers"),
    ("/analytics/api/margin/", "manager_headers"),
    ("/analytics/api/margin-by-day/", "manager_headers"),
]

LIMIT_ENDPOINTS = [
    ("/analytics/api/top-products/", "analyst_headers"),
    ("/analytics/api/top-customers/", "manager_headers"),
]

DATE_RANGE_ENDPOINTS = {
    "/analytics/api/revenue/",
    "/analytics/api/average-check/",
    "/analytics/api/margin/",
    "/analytics/api/margin-by-day/",
}

ANALYST_SHAPES = {
    "/analytics/api/revenue/": {"day", "revenue"},
    "/analytics/api/top-products/": {"product_name", "total_revenue", "total_quantity"},
    "/analytics/api/average-check/": {"average_check"},
    "/analytics/api/customers-by-city/": {"city", "total_customers", "total_orders"},
    "/analytics/api/funnel/": {"status_key", "status_name", "count", "conversion_rate"},
}

MANAGER_SHAPES = {
    "/analytics/api/margin/": {"total_revenue", "total_cost", "total_margin", "margin_percent"},
    "/analytics/api/margin-by-day/": {"day", "revenue", "cost", "margin", "margin_percent"},
    "/analytics/api/abc-analysis/": {"product_name", "revenue", "category", "cumulative_percent"},
    "/analytics/api/revenue-by-day-of-week/": {"period", "revenue", "order_count"},
    "/analytics/api/revenue-by-hour/": {"period", "revenue", "order_count"},
    "/analytics/api/revenue-by-months/": {"period", "revenue", "order_count"},
    "/analytics/api/top-customers/": {"full_name", "email", "city", "total_spent", "order_count", "last_order_date"},
}


def _assert_list_shape(payload, keys: set[str]) -> None:
    assert isinstance(payload, list) and len(payload) > 0
    for item in payload:
        assert set(item.keys()) == keys


def _date_range_params(url: str) -> dict[str, str] | None:
    if url in DATE_RANGE_ENDPOINTS:
        return {"start": "2026-01-01", "end": "2026-12-31"}
    return None


@pytest.fixture
def endpoint_headers(request):
    return request.getfixturevalue(request.param)


@pytest.mark.django_db
@pytest.mark.parametrize("url", ALL_ENDPOINTS)
class TestAuthentication:
    def test_requires_token(self, client, url):
        response = client.get(url)

        assert response.status_code == 401
        assert response.json()["success"] is False

    def test_rejects_invalid_token(self, client, url):
        response = client.get(url, HTTP_AUTHORIZATION="Token bogus")

        assert response.status_code == 401

    def test_analyst_token_access(self, client, analyst_headers, sample_data, url):
        response = client.get(url, **analyst_headers)

        expected = 200 if url in ANALYST_ENDPOINTS else 403
        assert response.status_code == expected

    def test_manager_token_has_hierarchical_access(self, client, manager_headers, sample_data, url):
        response = client.get(url, **manager_headers)

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url,keys", ANALYST_SHAPES.items())
def test_analyst_response_shape(client, analyst_headers, sample_data, url, keys):
    response = client.get(url, _date_range_params(url), **analyst_headers)

    assert response.status_code == 200
    if url == "/analytics/api/average-check/":
        assert set(response.json().keys()) == keys
    else:
        _assert_list_shape(response.json(), keys)


@pytest.mark.django_db
@pytest.mark.parametrize("url,keys", MANAGER_SHAPES.items())
def test_manager_response_shape(client, manager_headers, sample_data, url, keys):
    response = client.get(url, _date_range_params(url), **manager_headers)

    assert response.status_code == 200
    if url == "/analytics/api/margin/":
        assert set(response.json().keys()) == keys
    else:
        _assert_list_shape(response.json(), keys)


@pytest.mark.django_db
class TestParameters:
    def test_revenue_respects_date_range(self, client, analyst_headers, sample_data):
        response = client.get(
            "/analytics/api/revenue/",
            {"start": "2026-02-01", "end": "2026-02-28"},
            **analyst_headers,
        )

        assert response.status_code == 200
        assert response.json() == [{"day": "2026-02-15T00:00:00+00:00", "revenue": 60000.0}]

    def test_margin_by_day_respects_date_range(self, client, manager_headers, sample_data):
        response = client.get(
            "/analytics/api/margin-by-day/",
            {"start": "2026-01-01", "end": "2026-01-31"},
            **manager_headers,
        )

        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["day"] == "2026-01-10"

    def test_top_products_respects_limit(self, client, analyst_headers, sample_data):
        response = client.get("/analytics/api/top-products/", {"limit": "1"}, **analyst_headers)

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_top_customers_respects_limit(self, client, manager_headers, sample_data):
        response = client.get("/analytics/api/top-customers/", {"limit": "1"}, **manager_headers)

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_default_date_range_uses_last_30_days(self, client, analyst_headers, db):
        response = client.get("/analytics/api/revenue/", **analyst_headers)

        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.django_db
@pytest.mark.parametrize("url,endpoint_headers", DATE_ENDPOINTS, indirect=["endpoint_headers"])
def test_invalid_date_returns_400(client, url, endpoint_headers):
    response = client.get(url, {"start": "not-a-date", "end": "2026-01-31"}, **endpoint_headers)

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "error": "Параметры start/end должны быть датами в формате YYYY-MM-DD",
    }


@pytest.mark.django_db
@pytest.mark.parametrize("url,endpoint_headers", LIMIT_ENDPOINTS, indirect=["endpoint_headers"])
def test_invalid_limit_returns_400(client, url, endpoint_headers):
    response = client.get(url, {"limit": "abc"}, **endpoint_headers)

    assert response.status_code == 400
    assert response.json() == {"success": False, "error": "Параметр limit должен быть целым числом"}
