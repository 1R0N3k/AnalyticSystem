from datetime import date, datetime, timedelta
from . import queries
from .schemas import MarginDataPoint, MarginSummary, ABCProduct


def get_revenue_data(start_date: date, end_date: date) -> list[dict]:
    qs = queries.get_revenue_by_period(start_date, end_date)
    return [
        {
            "day": item["day"].isoformat(),
            "revenue": float(item["revenue"] or 0)
        }
        for item in qs
    ]


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


def get_margin_summary() -> MarginSummary:
    qs = queries.get_margin_summary(start_date, end_date)

    total_revenue = float(raw_data['total_revenue'] or 0)
    total_cost = float(raw_data['total_cost'] or 0)
    
    total_margin = total_revenue - total_cost
    margin_percent = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
    
    return MarginSummary(
        total_revenue=total_revenue,
        total_cost=total_cost,
        total_margin=total_margin,
        margin_percent=margin_percent
    )