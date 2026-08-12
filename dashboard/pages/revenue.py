import streamlit as st
import plotly.express as px
from datetime import date, timedelta
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth() 
st.set_page_config(layout="wide")
st.title("Выручка по периодам")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Дата начала",
            value=date.today() - timedelta(days=30),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today()
        )    
    with col2:
        end_date = st.date_input(
            "Дата окончания",
            value=date.today(),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today()            
        )

@st.cache_data(ttl=600)
def load_revenue_data(start_date: str, end_date: str) -> list[dict]:
    return api_client.get_revenue(
        start_date=start_date,
        end_date=end_date
    )

@st.cache_data(ttl=600)
def load_avg_check_data(start_date: str, end_date: str) -> list[dict]:
    return api_client.get_average_check(
        start_date=start_date,
        end_date=end_date
    )

with st.spinner("Загрузка данных из API..."):
    try:
        revenue_data = load_revenue_data(start_date.isoformat(), end_date.isoformat())
        avg_check_data = load_avg_check_data(start_date.isoformat(), end_date.isoformat())
        
        if not revenue_data:
            st.warning("Нет данных за выбранный период")
        else:
            total_revenue = sum(item['revenue'] for item in revenue_data)
            avg_check = avg_check_data['average_check']
            days_count = len(revenue_data)
            
            st.subheader("Ключевые показатели")
            col1, col2, col3 = st.columns(3, gap="large")
            with col1:
                st.metric("Общая выручка", f"{total_revenue:,.2f} ₽")
            with col2:
                st.metric("Средний чек", f"{avg_check:,.2f} ₽")
            with col3:
                st.metric("Дней с продажами", days_count)

            st.subheader("Динамика выручки")
            fig = px.line(
                revenue_data,
                x='day',
                y='revenue',
                title='Выручка по дням',
                labels={'day': 'Дата', 'revenue': 'Выручка (₽)'},
                markers=True
            )
            fig.update_layout(
                xaxis_title="Дата",
                yaxis_title="Выручка (₽)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Детализация по дням"):
                st.dataframe(revenue_data, use_container_width=True)

    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")