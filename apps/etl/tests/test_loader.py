from datetime import UTC, datetime
from decimal import Decimal

import pytest
from catalog.models import Category, Product
from customers.models import Customer
from etl.loader import load_order, load_orders
from etl.schemas import RawOrder, RawOrderItem
from orders.models import Order, OrderItem


def _make_raw_order(email: str = "ivan@example.com") -> RawOrder:
    return RawOrder(
        client_name="Иван",
        client_surname="Петров",
        client_email=email,
        city="Москва",
        items_list=[
            RawOrderItem(
                name="Смартфон", category="Электроника", quantity=2, price=Decimal("1000.00"), cost=Decimal("500.00")
            ),
            RawOrderItem(
                name="Футболка", category="Одежда", quantity=1, price=Decimal("800.00"), cost=Decimal("300.00")
            ),
        ],
        created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
        status="paid",
    )


@pytest.mark.django_db
class TestLoadOrder:
    def test_creates_all_records(self):
        load_order(_make_raw_order())

        assert Customer.objects.count() == 1
        assert Category.objects.count() == 2
        assert Product.objects.count() == 2
        assert Order.objects.count() == 1
        assert OrderItem.objects.count() == 2

    def test_computes_due_from_items(self):
        order = load_order(_make_raw_order())

        assert order.due == Decimal("2800.00")

    def test_reuses_customer_and_products(self):
        load_order(_make_raw_order())

        second_data = _make_raw_order().model_dump()
        second_data["created_at"] = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
        second_data["status"] = "delivered"
        load_order(RawOrder(**second_data))

        assert Customer.objects.count() == 1
        assert Product.objects.count() == 2
        assert Order.objects.count() == 2
        assert OrderItem.objects.count() == 4


@pytest.mark.django_db
class TestLoadOrders:
    def test_returns_loaded_count(self):
        raw_orders = [_make_raw_order("a@example.com"), _make_raw_order("b@example.com")]

        assert load_orders(raw_orders) == 2
        assert Customer.objects.count() == 2
