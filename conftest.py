from datetime import UTC, datetime
from decimal import Decimal

import pytest
from catalog.models import Category, Product
from customers.models import Customer
from django.contrib.auth.models import Group, User
from orders.models import Order, OrderItem

from apps.auth_api.models import AuthToken


def _create_user(username: str, password: str, *group_names: str) -> User:
    user = User.objects.create_user(username=username, password=password)
    for name in group_names:
        group, _ = Group.objects.get_or_create(name=name)
        user.groups.add(group)
    return user


@pytest.fixture
def analyst_user(db) -> User:
    return _create_user("analyst", "password123", "analyst")


@pytest.fixture
def manager_user(db) -> User:
    return _create_user("manager", "password123", "manager")


@pytest.fixture
def plain_user(db) -> User:
    return _create_user("plain", "password123")


@pytest.fixture
def analyst_headers(analyst_user: User) -> dict[str, str]:
    token = AuthToken.create_token(analyst_user, hours=24)
    return {"HTTP_AUTHORIZATION": f"Token {token.token}"}


@pytest.fixture
def manager_headers(manager_user: User) -> dict[str, str]:
    token = AuthToken.create_token(manager_user, hours=24)
    return {"HTTP_AUTHORIZATION": f"Token {token.token}"}


@pytest.fixture
def sample_data(db) -> dict:
    electronics = Category.objects.create(name="Электроника")
    clothes = Category.objects.create(name="Одежда")

    phone = Product.objects.create(
        category=electronics,
        name="Смартфон",
        price=Decimal("10000.00"),
        cost=Decimal("5000.00"),
    )
    laptop = Product.objects.create(
        category=electronics,
        name="Ноутбук",
        price=Decimal("50000.00"),
        cost=Decimal("30000.00"),
    )
    tshirt = Product.objects.create(
        category=clothes,
        name="Футболка",
        price=Decimal("1000.00"),
        cost=Decimal("400.00"),
    )

    ivan = Customer.objects.create(name="Иван", surname="Петров", email="ivan@example.com", city="Москва")
    maria = Customer.objects.create(name="Мария", surname="Сидорова", email="maria@example.com", city="Казань")

    orders = [
        Order.objects.create(
            customer=ivan,
            created_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
            status="paid",
            due=Decimal("11000.00"),
        ),
        Order.objects.create(
            customer=maria,
            created_at=datetime(2026, 2, 15, 18, 0, tzinfo=UTC),
            status="delivered",
            due=Decimal("60000.00"),
        ),
        Order.objects.create(
            customer=ivan,
            created_at=datetime(2026, 3, 20, 8, 0, tzinfo=UTC),
            status="new",
            due=Decimal("2000.00"),
        ),
        Order.objects.create(
            customer=maria,
            created_at=datetime(2026, 3, 20, 9, 0, tzinfo=UTC),
            status="cancelled",
            due=Decimal("5000.00"),
        ),
    ]

    OrderItem.objects.bulk_create(
        [
            OrderItem(order=orders[0], product=phone, quantity=1, price=Decimal("10000.00"), cost=Decimal("5000.00")),
            OrderItem(order=orders[0], product=tshirt, quantity=1, price=Decimal("1000.00"), cost=Decimal("400.00")),
            OrderItem(order=orders[1], product=laptop, quantity=1, price=Decimal("50000.00"), cost=Decimal("30000.00")),
            OrderItem(order=orders[1], product=tshirt, quantity=10, price=Decimal("1000.00"), cost=Decimal("400.00")),
            OrderItem(order=orders[2], product=phone, quantity=2, price=Decimal("10000.00"), cost=Decimal("5000.00")),
        ]
    )

    return {"orders": orders}
