from datetime import date, timedelta
from django.db.models import Sum, Count, Avg, F, Window
from django.db.models.functions import TruncDay, RowNumber

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


def _get_products_revenue_base_queryset():
    return OrderItem.objects.filter(
        order__status__in=['paid', 'delivered']
    ).values(
        product_name=F('product__name')
    ).annotate(
        total_revenue=Sum(F('price') * F('quantity')),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue') 

def get_top_products(limit: int = 10):
    return _get_products_revenue_base_queryset()[:limit]

def get_all_products_with_revenue():
    return _get_products_revenue_base_queryset()


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


def get_margin_summary(start_date: date, end_date: date):
    return OrderItem.objects.filter(
        order__created_at__date__range=[start_date, end_date],
        order__status__in=['paid', 'delivered']
    ).aggregate(
        total_revenue=Sum(F('price') * F('quantity')),
        total_cost=Sum(F('cost') * F('quantity')),
    )
   
def get_margin_by_day(start_date: date, end_date: date) -> list[MarginDataPoint]:
    return OrderItem.objects.filter(
        order__created_at__date__range=[start_date, end_date],
        order__status__in=['paid', 'delivered']
    ).annotate(
        day=TruncDay('order__created_at')
    ).values('day').annotate(
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('cost') * F('quantity'))
    ).order_by('day')


def get_order_status_counts():
    return Order.objects.values('status').annotate(
        count=Count('id')
    )


def get_revenue_by_day_of_week():
    ...

def get_revenue_by_hour():
    ...


def get_top_customers():
    ...