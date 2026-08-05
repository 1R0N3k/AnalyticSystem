from datetime import date, datetime, timedelta
from . import queries


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