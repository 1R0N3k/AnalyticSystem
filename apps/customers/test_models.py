from datetime import UTC, datetime
from decimal import Decimal

import pytest
from customers.models import Customer
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from orders.models import Order


@pytest.mark.django_db
class TestCustomer:
    def test_str(self):
        customer = Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")

        assert str(customer) == "Иван Петров (ivan@example.com) from Москва"

    def test_email_is_unique(self):
        Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")

        with pytest.raises(IntegrityError):
            Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Казань")

    def test_protected_from_deletion_with_orders(self):
        customer = Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")
        Order.objects.create(
            customer=customer,
            created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
            status="new",
            due=Decimal("100.00"),
        )

        with pytest.raises(ProtectedError):
            customer.delete()
