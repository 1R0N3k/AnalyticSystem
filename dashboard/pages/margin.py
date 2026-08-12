import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth() 
st.set_page_config(layout="wide")
st.title("Финансы и Маржинальность")

st.markdown("Анализ реальной прибыльности бизнеса. Учитываются только оплаченные и доставленные заказы.")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Дата начала", value=date.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("Дата окончания", value=date.today())

@st.cache_data(ttl=600)
def load_margin_summary_data(start_date: str, end_date: str):
    return api_client.get_margin(start_date, end_date)

@st.cache_data(ttl=600)
def load_margin_by_day_data(start_date: str, end_date: str):
    return api_client.get_margin_by_day(start_date, end_date)

with st.spinner("Загрузка данных..."):
    try:
        summary = load_margin_summary_data(start_date.isoformat(), end_date.isoformat())
        daily_data = load_margin_by_day_data(start_date.isoformat(), end_date.isoformat())
        
        if not daily_data:
            st.warning("Нет данных за выбранный период")
        else:
            df_daily = pd.DataFrame(daily_data)
            
            st.subheader("Ключевые показатели за период")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Выручка", f"{summary['total_revenue']:,.0f} ₽")
            kpi2.metric("Себестоимость", f"{summary['total_cost']:,.0f} ₽")
            kpi3.metric("Валовая маржа", f"{summary['total_margin']:,.0f} ₽")
            kpi4.metric("Рентабельность", f"{summary['margin_percent']:.1f}%")
            
            st.divider()
            
            st.subheader("Динамика выручки и маржи по дням")
            fig = px.line(
                df_daily,
                x='day',
                y=['revenue', 'margin'],
                labels={'day': 'Дата', 'value': 'Сумма (₽)'},
                color_discrete_map={'revenue': '#1f77b4', 'margin': '#2ca02c'},
                markers=True
            )
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Детализация по дням"):
                st.dataframe(df_daily, use_container_width=True, hide_index=True)
                
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")