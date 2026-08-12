import requests
from typing import Optional
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000/analytics/api"
AUTH_API_BASE_URL = "http://127.0.0.1:8000/api/auth"

def get_auth_headers() -> dict:
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Token {token}"}
    return {}


def login_user(username: str, password: str) -> bool:
    response = requests.post(
        f"{AUTH_API_BASE_URL}/login/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        st.session_state.auth_token = data["token"]
        st.session_state.username = data["username"]
        st.session_state.roles = data["roles"]
        return True
    else:
        st.error(response.json().get("error", "Ошибка входа"))
        return False


def logout_user():
    token = st.session_state.get("auth_token")
    if token:
        requests.post(f"{AUTH_API_BASE_URL}/logout/", headers={"Authorization": f"Token {token}"})
    
    for key in ["auth_token", "username", "roles"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

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

    response = requests.get(f"{API_BASE_URL}/margin/", params=params, headers=get_auth_headers())
    
    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return {}
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return {}

    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_margin_by_day(start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
    params = {}
    if start_date:
        params['start'] = start_date
    if end_date:
        params['end'] = end_date

    response = requests.get(f"{API_BASE_URL}/margin-by-day/", params=params, headers=get_auth_headers())
    
    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_abc_analysis() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/abc-analysis/", headers=get_auth_headers())
    
    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_funnel_data() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/funnel/")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_day_of_week() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-day-of-week/", headers=get_auth_headers())
    
    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_hour() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-hour/", headers=get_auth_headers())

    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_revenue_by_month() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/revenue-by-months/", headers=get_auth_headers())

    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=600)
def get_top_customers_data(limit: int = 100) -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/top-customers/", params={'limit': limit}, headers=get_auth_headers())

    if response.status_code == 401:
        st.error("Сессия истекла. Пожалуйста, войдите снова.")
        logout_user()
        return []
    if response.status_code == 403:
        error_msg = response.json().get('error', 'Доступ запрещён')
        st.error(f"{error_msg}")
        return []
    response.raise_for_status()
    return response.json()