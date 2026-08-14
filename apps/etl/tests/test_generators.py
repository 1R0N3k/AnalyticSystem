from etl.generators import CITIES, PRODUCT_CATALOG, STATUS_WEIGHTS, generate_mock_orders


class TestGenerateMockOrders:
    def test_generates_requested_count(self):
        orders = generate_mock_orders(25)

        assert len(orders) == 25

    def test_orders_have_valid_structure(self):
        order = generate_mock_orders(1)[0]

        assert order.status in STATUS_WEIGHTS
        assert order.city in CITIES
        assert 1 <= len(order.items_list) <= 5

    def test_items_are_consistent_with_catalog(self):
        order = generate_mock_orders(1)[0]

        for item in order.items_list:
            assert item.category in PRODUCT_CATALOG
            catalog_names = [name for name, *_ in PRODUCT_CATALOG[item.category]]
            assert item.name in catalog_names
            assert 1 <= item.quantity <= 5
            assert item.price > 0
            assert 0 < item.cost < item.price
