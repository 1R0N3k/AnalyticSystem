from datetime import date
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDay

from orders.models import Order, OrderItem
from customers.models import Customer


def get_revenue_by_period(start_date: date, end_date: date):
    return Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        status__in=['paid', 'delivered']
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        revenue=Sum('due')
    ).order_by('day')


def get_top_products(limit: int = 10):
    return OrderItem.objects.filter(
        order__status__in=['paid', 'delivered']
    ).values(
        product_name=F('product__name')
    ).annotate(
        total_revenue=Sum(F('price') * F('quantity')),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')[:limit]


def get_average_check(start_date: date, end_date: date):
    result = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        status__in=['paid', 'delivered']
    ).aggregate(
        avg_check=Avg('due')
    )
    return result['avg_check'] or 0.0


def get_customers_by_city():
    return Customer.objects.values('city').annotate(
        total_customers=Count('id', distinct=True),
        total_orders=Count('orders', distinct=True)
    ).order_by('-total_orders')