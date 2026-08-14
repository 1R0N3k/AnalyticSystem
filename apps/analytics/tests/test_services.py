from datetime import date

import pytest
from analytics import services


def _day(date_str: str) -> str:
    return f"{date_str}T00:00:00+00:00"


@pytest.mark.django_db
class TestRevenueData:
    def test_returns_daily_revenue_for_paid_and_delivered(self, sample_data):
        data = services.get_revenue_data(date(2026, 1, 1), date(2026, 12, 31))

        assert data == [
            {"day": _day("2026-01-10"), "revenue": 11000.0},
            {"day": _day("2026-02-15"), "revenue": 60000.0},
        ]

    def test_filters_by_date_range(self, sample_data):
        data = services.get_revenue_data(date(2026, 2, 1), date(2026, 2, 28))

        assert data == [{"day": _day("2026-02-15"), "revenue": 60000.0}]

    def test_empty_period_returns_empty_list(self, sample_data):
        assert services.get_revenue_data(date(2025, 1, 1), date(2025, 1, 31)) == []


@pytest.mark.django_db
class TestTopProducts:
    def test_returns_products_sorted_by_revenue(self, sample_data):
        data = services.get_top_products_data()

        assert data == [
            {"product_name": "Ноутбук", "total_revenue": 50000.0, "total_quantity": 1},
            {"product_name": "Футболка", "total_revenue": 11000.0, "total_quantity": 11},
            {"product_name": "Смартфон", "total_revenue": 10000.0, "total_quantity": 1},
        ]

    def test_respects_limit(self, sample_data):
        data = services.get_top_products_data(limit=2)

        assert [item["product_name"] for item in data] == ["Ноутбук", "Футболка"]


@pytest.mark.django_db
class TestAverageCheck:
    def test_average_check_over_period(self, sample_data):
        assert services.get_average_check_data(date(2026, 1, 1), date(2026, 12, 31)) == {"average_check": 35500.0}

    def test_average_check_zero_without_orders(self, sample_data):
        assert services.get_average_check_data(date(2025, 1, 1), date(2025, 1, 31)) == {"average_check": 0.0}


@pytest.mark.django_db
class TestCustomersByCity:
    def test_groups_customers_and_orders_by_city(self, sample_data):
        data = services.get_customers_by_city_data()
        by_city = {item["city"]: item for item in data}

        assert by_city["Москва"] == {"city": "Москва", "total_customers": 1, "total_orders": 2}
        assert by_city["Казань"] == {"city": "Казань", "total_customers": 1, "total_orders": 2}

    def test_returns_empty_list_without_customers(self, db):
        assert services.get_customers_by_city_data() == []


@pytest.mark.django_db
class TestMargin:
    def test_margin_summary(self, sample_data):
        summary = services.get_margin_summary(date(2026, 1, 1), date(2026, 12, 31))

        assert summary.total_revenue == 71000.0
        assert summary.total_cost == 39400.0
        assert summary.total_margin == 31600.0
        assert summary.margin_percent == pytest.approx(44.5070, abs=0.01)

    def test_margin_summary_empty_period_returns_zeros(self, sample_data):
        summary = services.get_margin_summary(date(2025, 1, 1), date(2025, 1, 31))

        assert summary.model_dump() == {
            "total_revenue": 0.0,
            "total_cost": 0.0,
            "total_margin": 0.0,
            "margin_percent": 0.0,
        }

    def test_margin_by_day(self, sample_data):
        data = services.get_margin_by_day(date(2026, 1, 1), date(2026, 12, 31))

        assert len(data) == 2
        day1, day2 = data
        assert day1.day.isoformat() == "2026-01-10"
        assert day1.revenue == 11000.0
        assert day1.cost == 5400.0
        assert day1.margin == 5600.0
        assert day1.margin_percent == pytest.approx(50.9091, abs=0.01)
        assert day2.margin_percent == pytest.approx(43.3333, abs=0.01)


@pytest.mark.django_db
class TestABCAnalysis:
    def test_abc_classification_boundaries(self, sample_data):
        data = services.get_abc_analysis()
        by_name = {item.product_name: item for item in data}

        assert by_name["Ноутбук"].category == "A"
        assert by_name["Ноутбук"].cumulative_percent == pytest.approx(70.4225, abs=0.01)
        assert by_name["Футболка"].category == "B"
        assert by_name["Футболка"].cumulative_percent == pytest.approx(85.9155, abs=0.01)
        assert by_name["Смартфон"].category == "C"
        assert by_name["Смартфон"].cumulative_percent == pytest.approx(100.0, abs=0.01)

    def test_abc_without_orders_returns_empty(self, db):
        assert services.get_abc_analysis() == []


@pytest.mark.django_db
class TestFunnel:
    def test_funnel_contains_all_stages(self, sample_data):
        data = services.get_funnel_data()

        assert [stage.status_key for stage in data] == ["new", "paid", "delivered", "cancelled"]
        assert [stage.status_name for stage in data] == ["Новый", "Оплачен", "Доставлен", "Отменён"]
        for stage in data:
            assert stage.count == 1
            assert stage.conversion_rate == 25.0

    def test_funnel_without_orders_returns_zero_conversion(self, db):
        data = services.get_funnel_data()

        assert all(stage.count == 0 and stage.conversion_rate == 0.0 for stage in data)


@pytest.mark.django_db
class TestTemporalAnalytics:
    def test_revenue_by_day_of_week_is_sorted_from_monday(self, sample_data):
        data = services.get_revenue_by_day_of_week()

        assert [item.period for item in data] == ["Суббота", "Воскресенье"]
        assert data[0].revenue == 11000.0
        assert data[0].order_count == 1
        assert data[1].revenue == 60000.0

    def test_revenue_by_hour_formats_and_sorts(self, sample_data):
        data = services.get_revenue_by_hour()

        assert [item.period for item in data] == ["12:00", "18:00"]
        assert data[0].revenue == 11000.0
        assert data[1].revenue == 60000.0

    def test_revenue_by_month_formats_names(self, sample_data):
        data = services.get_revenue_by_month()

        assert [item.period for item in data] == ["Январь 2026", "Февраль 2026"]
        assert data[0].revenue == 11000.0
        assert data[1].revenue == 60000.0


@pytest.mark.django_db
class TestTopCustomers:
    def test_top_customers_sorted_by_spent(self, sample_data):
        data = services.get_top_customers_data()

        assert len(data) == 2
        assert data[0].full_name == "Мария Сидорова"
        assert data[0].total_spent == 60000.0
        assert data[0].order_count == 1
        assert data[0].last_order_date.isoformat() == "2026-02-15"
        assert data[1].full_name == "Иван Петров"
        assert data[1].total_spent == 11000.0
        assert data[1].last_order_date.isoformat() == "2026-01-10"

    def test_top_customers_respects_limit(self, sample_data):
        data = services.get_top_customers_data(limit=1)

        assert len(data) == 1
        assert data[0].full_name == "Мария Сидорова"
