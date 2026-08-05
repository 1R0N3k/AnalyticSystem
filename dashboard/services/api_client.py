import requests
from typing import Optional


API_BASE_URL = "http://127.0.0.1:8000/analytics/api"


def get_revenue(start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date
    
    response = requests.get(f"{API_BASE_URL}/revenue/", params=params)
    response.raise_for_status()
    return response.json()


def get_top_products(limit: int = 10) -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/top-products/", params={'limit': limit})
    response.raise_for_status()
    return response.json()


def get_average_check(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date
    
    response = requests.get(f"{API_BASE_URL}/average-check/", params=params)
    response.raise_for_status()
    return response.json()


def get_customers_by_city() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/customers-by-city/")
    response.raise_for_status()
    return response.json()