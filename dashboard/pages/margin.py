import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
from datetime import date, timedelta
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard


st.set_page_config(
    page_title="Финансы и Маржинальность",
    page_icon="💰"
)
auth_guard.require_auth(required_role='manager')


@st.cache_data(ttl=60)
def load_margin_summary_data(start_date: str, end_date: str) -> dict:
    return api_client.get_margin(start_date, end_date)

@st.cache_data(ttl=60)
def load_margin_by_day_data(start_date: str, end_date: str) -> list[dict]:
    return api_client.get_margin_by_day(start_date, end_date)


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("💰 Финансы и Маржинальность")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            st.cache_data.clear()
            st.rerun()

st.markdown("Анализ реальной прибыльности бизнеса. Учитываются только оплаченные и доставленные заказы.")


with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Дата начала",
            value=date.today() - timedelta(days=30),
            help="Начальная дата периода анализа"
        )
    with col2:
        end_date = st.date_input(
            "Дата окончания",
            value=date.today(),
            help="Конечная дата периода анализа"
        )


with st.spinner("Загрузка данных из API..."):
    try:
        summary = load_margin_summary_data(start_date.isoformat(), end_date.isoformat())
        daily_data = load_margin_by_day_data(start_date.isoformat(), end_date.isoformat())
        
        if not summary or not daily_data:
            st.warning("Нет данных за выбранный период или доступ ограничен.")
            st.stop()
        
        df_daily = pd.DataFrame(daily_data)
        
        avg_daily_revenue = summary['total_revenue'] / len(df_daily) if len(df_daily) > 0 else 0
        best_day = df_daily.loc[df_daily['revenue'].idxmax()]
        
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API.")
        st.stop()
    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")
        st.stop()


with st.container(border=True):
    st.subheader("Ключевые показатели за период")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Выручка", f"{summary['total_revenue']:,.0f} ₽")
    with col2:
        st.metric("📉 Себестоимость", f"{summary['total_cost']:,.0f} ₽")
    with col3:
        st.metric("📈 Валовая маржа", f"{summary['total_margin']:,.0f} ₽")
    with col4:
        st.metric("📊 Рентабельность", f"{summary['margin_percent']:.1f}%")


with st.container(border=True):
    st.subheader("Динамика выручки и маржи по дням")
    fig = px.line(
        df_daily,
        x='day',
        y=['revenue', 'margin'],
        labels={'day': 'Дата', 'value': 'Сумма (₽)'},
        color_discrete_map={'revenue': '#1f77b4', 'margin': '#2ca02c'},
        markers=True
    )
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Показатель'
    )
    st.plotly_chart(fig)


with st.expander("Детализация"):
    st.dataframe(
        df_daily,
        hide_index=True,
        column_config={
            "day": st.column_config.DateColumn("Дата", format="DD.MM.YYYY"),
            "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
            "margin": st.column_config.NumberColumn("Маржа", format="%.2f ₽"),
        }
    )