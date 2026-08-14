import pytest
from catalog.models import Category, Product
from customers.models import Customer
from django.core.management import call_command
from django.core.management.base import CommandError
from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestRunEtlCommand:
    def test_loads_requested_number_of_orders(self):
        call_command("run_etl", rows=5, batch_size=5)

        assert Order.objects.count() == 5
        assert 5 <= OrderItem.objects.count() <= 25
        assert Category.objects.count() >= 1
        assert Product.objects.count() >= 1
        assert Customer.objects.count() >= 1

    def test_zero_rows_raises_error(self):
        with pytest.raises(CommandError):
            call_command("run_etl", rows=0)

    def test_zero_batch_size_raises_error(self):
        with pytest.raises(CommandError):
            call_command("run_etl", rows=5, batch_size=0)

    def test_clear_removes_existing_data(self, sample_data):
        call_command("run_etl", rows=2, batch_size=2, clear=True)

        assert Customer.objects.filter(email__in=["ivan@example.com", "maria@example.com"]).count() == 0
        assert Order.objects.count() == 2
