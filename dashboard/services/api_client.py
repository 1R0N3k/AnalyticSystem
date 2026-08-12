import requests
from typing import Optional
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000/analytics/api"

@st.cache_data(ttl=600)
def get_revenue(start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date
    
    response = requests.get(f"{API_BASE_URL}/revenue/", params=params)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=600)
def get_top_products(limit: int = 10) -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/top-products/", params={'limit': limit})
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=600)
def get_average_check(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date
    
    response = requests.get(f"{API_BASE_URL}/average-check/", params=params)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=600)
def get_customers_by_city() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/customers-by-city/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_margin(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date

    response = requests.get(f"{API_BASE_URL}/margin/", params=params)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_margin_by_day(start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date

    response = requests.get(f"{API_BASE_URL}/margin-by-day/", params=params)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_abc_analysis() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/abc-analysis/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_funnel_data() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/funnel/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_day_of_week() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-day-of-week/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_hour() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-hour/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_month() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-months/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_top_customers_data(limit: int = 100) -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/top-customers/", params={'limit': limit})
    response.raise_for_status()
    return response.json()