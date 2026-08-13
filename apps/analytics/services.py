from datetime import date

from orders.models import Order

from . import queries
from .schemas import ABCProduct, FunnelStage, MarginDataPoint, MarginSummary, TimeDataPoint, TopCustomer


def get_revenue_data(start_date: date, end_date: date) -> list[dict]:
    qs = queries.get_revenue_by_period(start_date, end_date)
    return [
        {
            "day": item["day"].isoformat(),
            "revenue": float(item["revenue"] or 0)
        }
        for item in qs
    ]


def get_average_check_data(start_date: date, end_date: date) -> dict:
    avg = queries.get_average_check(start_date, end_date)
    return {"average_check": float(avg)}


def get_customers_by_city_data() -> list[dict]:
    qs = queries.get_customers_by_city()
    return [
        {
            "city": item["city"] or "Не указан",
            "total_customers": item["total_customers"],
            "total_orders": item["total_orders"]
        }
        for item in qs
    ]


def get_margin_by_day(start_date: date, end_date: date) -> list[MarginDataPoint]:
    qs = queries.get_margin_by_day(start_date, end_date)

    result = []
    for item in qs:
        revenue = float(item['revenue'] or 0)
        cost = float(item['cost'] or 0)

        margin=revenue - cost
        margin_percent = (margin / revenue * 100) if revenue > 0 else 0

        result.append(
            MarginDataPoint(
                day=item['day'],
                revenue=revenue,
                cost=cost,
                margin=margin,
                margin_percent=margin_percent
            )
        )
    return result


def get_margin_summary(start_date: date, end_date: date) -> MarginSummary:
    qs = queries.get_margin_summary(start_date, end_date)

    total_revenue = float(qs['total_revenue'] or 0)
    total_cost = float(qs['total_cost'] or 0)

    total_margin = total_revenue - total_cost
    margin_percent = (total_margin / total_revenue * 100) if total_revenue > 0 else 0

    return MarginSummary(
        total_revenue=total_revenue,
        total_cost=total_cost,
        total_margin=total_margin,
        margin_percent=margin_percent
    )


def get_top_products_data(limit: int = 10) -> list[dict]:
    qs = queries.get_top_products(limit)
    return [
        {
            "product_name": item["product_name"],
            "total_revenue": float(item["total_revenue"] or 0),
            "total_quantity": item["total_quantity"] or 0
        }
        for item in qs
    ]


def get_abc_analysis() -> list[ABCProduct]:
    qs = queries.get_all_products_with_revenue()

    total_revenue = sum(float(item['total_revenue'] or 0) for item in qs)

    result = []
    cumulative_revenue: float = 0.0
    for item in qs:
        revenue = float(item['total_revenue'] or 0)
        cumulative_revenue += revenue
        percent = (cumulative_revenue * 100 / total_revenue) if total_revenue > 0 else 0

        if percent <= 80:
            category = 'A'
        elif percent <= 95:
            category = 'B'
        else:
            category = 'C'

        result.append(ABCProduct(
            product_name=item['product_name'],
            revenue=revenue,
            category=category,
            cumulative_percent=percent
        ))
    return result


def get_funnel_data() -> list[FunnelStage]:
    qs = queries.get_order_status_counts()

    status_counts = {item['status']: item['count'] for item in qs}
    stages_order = ['new', 'paid', 'delivered', 'cancelled']

    result = []
    for stage_key in stages_order:
        count = status_counts.get(stage_key, 0)

        status_name = dict(Order.Status.choices).get(stage_key, stage_key.capitalize())

        total_all_orders = sum(status_counts.values())
        conversion_rate = count / total_all_orders * 100 if total_all_orders > 0 else 0.0

        result.append(FunnelStage(
            status_key=stage_key,
            status_name=status_name,
            count=count,
            conversion_rate=round(conversion_rate, 2)
        ))

    return result


def get_revenue_by_day_of_week() -> list[TimeDataPoint]:
    qs = queries.get_revenue_by_day_of_week()
    day_names = {
        1: 'Воскресенье',
        2: 'Понедельник',
        3: 'Вторник',
        4: 'Среда',
        5: 'Четверг',
        6: 'Пятница',
        7: 'Суббота'
    }

    result = []
    for item in qs:
        day_num = item['day_of_week']
        result.append(TimeDataPoint(
            period=day_names.get(day_num, f'День {day_num}'),
            revenue=float(item['revenue'] or 0),
            order_count=item['order_count'] or 0
        ))

    order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    result.sort(key=lambda x: order.index(x.period) if x.period in order else 999)

    return result


def get_revenue_by_hour() -> list[TimeDataPoint]:
    qs = queries.get_revenue_by_hour()

    result = []
    for item in qs:
        hour = item['hour']
        result.append(TimeDataPoint(
            period=f'{hour:02d}:00',
            revenue=float(item['revenue'] or 0),
            order_count=item['order_count'] or 0
        ))

    result.sort(key=lambda x: int(x.period.split(':')[0]))

    return result


def get_revenue_by_month() -> list[TimeDataPoint]:
    qs = queries.get_revenue_by_month()

    month_names = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }

    result = []
    for item in qs:
        month_date = item['month']
        month_num = month_date.month
        year = month_date.year

        result.append(TimeDataPoint(
            period=f'{month_names.get(month_num, "")} {year}',
            revenue=float(item['revenue'] or 0),
            order_count=item['order_count'] or 0
        ))

    result.sort(key=lambda x: next((item['month'] for item in qs
                                    if f'{month_names.get(item["month"].month, "")} {item["month"].year}' == x.period), 0))

    return result


def get_top_customers_data(limit: int = 100) -> list[TopCustomer]:
    qs = queries.get_top_customers(limit)

    result = []
    for item in qs:
        last_date = item.last_order_date.date() if item.last_order_date else None

        result.append(TopCustomer(
            full_name=item.full_name,
            email=item.email,
            city=item.city,
            total_spent=float(item.total_spent or 0),
            order_count=item.order_count or 0,
            last_order_date=last_date
        ))

    return result
