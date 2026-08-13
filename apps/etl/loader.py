from catalog.models import Category, Product
from customers.models import Customer
from django.db import transaction
from orders.models import Order, OrderItem

from .schemas import RawOrder


@transaction.atomic
def load_order(raw_order: RawOrder) -> Order:
    customer, _ = Customer.objects.get_or_create(
        email=raw_order.client_email,
        defaults={
            'name': raw_order.client_name,
            'surname': raw_order.client_surname,
            'city': raw_order.city,
        }
    )

    total_amount = sum(
        item.price * item.quantity
        for item in raw_order.items_list
    )

    order = Order.objects.create(
        customer=customer,
        created_at=raw_order.created_at,
        status=raw_order.status,
        due=total_amount,
    )

    order_items = []
    for item in raw_order.items_list:
        category, _ = Category.objects.get_or_create(
            name=item.category,
        )

        product, _ = Product.objects.get_or_create(
            name=item.name,
            defaults={
                'category': category,
                'price': item.price,
                'cost': item.cost,
            }
        )

        order_items.append(OrderItem(
            order=order,
            product=product,
            quantity=item.quantity,
            price=item.price,
            cost=item.cost
        ))

    OrderItem.objects.bulk_create(order_items)

    return order


def load_orders(orders: list[RawOrder]) -> int:
    loaded_count = 0
    for raw_order in orders:
        try:
            load_order(raw_order)
            loaded_count += 1
        except Exception as e:
            print(f"Ошибка при загрузке заказа: {e}")
            continue

    return loaded_count
