from datetime import UTC, datetime
from decimal import Decimal

import pytest
from etl.schemas import RawOrder, RawOrderItem
from pydantic import ValidationError


def _valid_item(**overrides) -> RawOrderItem:
    data = dict(name="Смартфон", category="Электроника", quantity=2, price=Decimal("100.50"), cost=Decimal("60.00"))
    data.update(overrides)
    return RawOrderItem(**data)


class TestRawOrderItem:
    def test_valid_item(self):
        item = _valid_item()

        assert item.quantity == 2

    @pytest.mark.parametrize(
        "overrides",
        [{"quantity": 0}, {"price": Decimal("0")}, {"cost": Decimal("-1")}, {"name": "X"}],
        ids=["zero-quantity", "zero-price", "negative-cost", "short-name"],
    )
    def test_rejects_invalid_item(self, overrides):
        with pytest.raises(ValidationError):
            _valid_item(**overrides)


class TestRawOrder:
    def _valid_order(self, **overrides) -> RawOrder:
        data = dict(
            client_name="Иван",
            client_surname="Петров",
            client_email="ivan@example.com",
            city="Москва",
            items_list=[_valid_item()],
            created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
        )
        data.update(overrides)
        return RawOrder(**data)

    def test_default_status_is_paid(self):
        order = self._valid_order()

        assert order.status == "paid"

    def test_custom_status_accepted(self):
        order = self._valid_order(status="cancelled")

        assert order.status == "cancelled"

    def test_rejects_unknown_status(self):
        with pytest.raises(ValidationError):
            self._valid_order(status="refunded")

    def test_rejects_invalid_email(self):
        with pytest.raises(ValidationError):
            self._valid_order(client_email="not-an-email")
