from decimal import Decimal

import pytest
from catalog.models import Category, Product
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError


def _product(category: Category, name: str) -> Product:
    return Product.objects.create(category=category, name=name, price=Decimal("100.00"), cost=Decimal("50.00"))


@pytest.mark.django_db
class TestCategory:
    def test_str(self):
        category = Category.objects.create(name="Электроника")

        assert str(category) == "Электроника"

    def test_name_is_unique(self):
        Category.objects.create(name="Электроника")

        with pytest.raises(IntegrityError):
            Category.objects.create(name="Электроника")

    def test_protected_from_deletion_with_products(self):
        category = Category.objects.create(name="Электроника")
        _product(category, "Смартфон")

        with pytest.raises(ProtectedError):
            category.delete()


@pytest.mark.django_db
class TestProduct:
    def test_str(self):
        category = Category.objects.create(name="Электроника")
        product = _product(category, "Смартфон")

        assert str(product) == "Смартфон"

    def test_name_is_unique(self):
        category = Category.objects.create(name="Электроника")
        _product(category, "Смартфон")

        with pytest.raises(IntegrityError):
            _product(category, "Смартфон")
