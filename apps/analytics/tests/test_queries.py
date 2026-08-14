from datetime import date
from decimal import Decimal

import pytest
from analytics import queries


@pytest.mark.django_db
class TestQueries:
    def test_revenue_by_period_excludes_new_and_cancelled(self, sample_data):
        qs = list(queries.get_revenue_by_period(date(2026, 1, 1), date(2026, 12, 31)))

        assert len(qs) == 2
        assert qs[0]["day"].date().isoformat() == "2026-01-10"
        assert qs[0]["revenue"] == Decimal("11000.00")
        assert qs[1]["revenue"] == Decimal("60000.00")

    def test_margin_summary_sums_price_times_quantity(self, sample_data):
        result = queries.get_margin_summary(date(2026, 1, 1), date(2026, 12, 31))

        assert result == {"total_revenue": Decimal("71000.00"), "total_cost": Decimal("39400.00")}

    def test_order_status_counts(self, sample_data):
        counts = {row["status"]: row["count"] for row in queries.get_order_status_counts()}

        assert counts == {"new": 1, "paid": 1, "delivered": 1, "cancelled": 1}

    def test_top_products_limited(self, sample_data):
        rows = list(queries.get_top_products(limit=1))

        assert len(rows) == 1
        assert rows[0]["product_name"] == "Ноутбук"
        assert rows[0]["total_revenue"] == Decimal("50000.00")
