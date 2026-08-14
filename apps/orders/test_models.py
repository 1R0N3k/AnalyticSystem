from datetime import UTC, datetime
from decimal import Decimal

import pytest
from catalog.models import Category, Product
from customers.models import Customer
from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrder:
    def _order(self, **overrides) -> Order:
        customer = Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")
        data = dict(
            customer=customer,
            created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
            status="paid",
            due=Decimal("100.00"),
        )
        data.update(overrides)
        data = {key: value for key, value in data.items() if value is not None}
        return Order.objects.create(**data)

    def test_default_status_is_new(self):
        order = self._order(status=None)

        assert order.status == "new"

    def test_str(self):
        order = self._order()

        assert "Заказ #" in str(order)
        assert "100.00" in str(order)

    def test_items_cascade_on_order_delete(self):
        order = self._order()
        category = Category.objects.create(name="Электроника")
        product = Product.objects.create(
            category=category, name="Смартфон", price=Decimal("100.00"), cost=Decimal("50.00")
        )
        OrderItem.objects.create(
            order=order, product=product, quantity=1, price=Decimal("100.00"), cost=Decimal("50.00")
        )

        order.delete()

        assert OrderItem.objects.count() == 0


@pytest.mark.django_db
class TestOrderItem:
    def test_str(self):
        customer = Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")
        category = Category.objects.create(name="Электроника")
        product = Product.objects.create(
            category=category, name="Смартфон", price=Decimal("100.00"), cost=Decimal("50.00")
        )
        order = Order.objects.create(
            customer=customer,
            created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
            status="paid",
            due=Decimal("200.00"),
        )
        item = OrderItem.objects.create(
            order=order, product=product, quantity=2, price=Decimal("100.00"), cost=Decimal("50.00")
        )

        assert str(item) == "Смартфон x2 = 200.00₽"
