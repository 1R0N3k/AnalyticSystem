import os
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth(required_role='manager')
st.set_page_config(
    page_title="Временная аналитика продаж",
    page_icon="⏰"
)

@st.cache_data(ttl=60)
def load_revenue_by_day_of_week_data() -> list[dict]:
    return api_client.get_revenue_by_day_of_week()

@st.cache_data(ttl=60)
def load_revenue_by_hours_data() -> list[dict]:
    return api_client.get_revenue_by_hour()

@st.cache_data(ttl=60)
def load_revenue_by_month() -> list[dict]:
    return api_client.get_revenue_by_month()


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("⏰ Временная аналитика продаж")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            load_revenue_by_day_of_week_data.clear()
            load_revenue_by_hours_data.clear()
            load_revenue_by_month.clear()
            st.rerun()

st.markdown("Анализ паттернов покупок: какие дни, часы и месяцы приносят больше всего выручки.")


with st.spinner("Загрузка данных из API..."):
    try:
        days_data = load_revenue_by_day_of_week_data()
        hours_data = load_revenue_by_hours_data()
        months_data = load_revenue_by_month()

        if not days_data or not hours_data or not months_data:
            st.warning("Нет данных для отображения или доступ ограничен.")
            st.stop()

        df_days = pd.DataFrame(days_data)
        df_hours = pd.DataFrame(hours_data)
        df_months = pd.DataFrame(months_data)

        total_revenue = df_months['revenue'].sum()
        total_orders = df_months['order_count'].sum()

        best_day = df_days.loc[df_days['revenue'].idxmax()]
        best_hour = df_hours.loc[df_hours['revenue'].idxmax()]

    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API.")
        st.stop()
    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")
        st.stop()


with st.container(border=True):
    st.subheader("Ключевые показатели")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Общая выручка", f"{total_revenue:,.0f} ₽")
    with col2:
        st.metric("📦 Всего заказов", f"{total_orders:,}")
    with col3:
        st.metric("📅 Лучший день", f"{best_day['period']}")
    with col4:
        st.metric("🕒 Пиковый час", f"{best_hour['period']}")


tab1, tab2, tab3 = st.tabs(["📅 По дням недели", "🕒 По часам", "🗓️ По месяцам"])

with tab1:
    with st.container(border=True):
        st.subheader("Выручка по дням недели")
        fig_days = px.bar(
            df_days, x='period', y='revenue',
            color='revenue',
            labels={'period': 'День недели', 'revenue': 'Выручка (₽)'},
            text='order_count'
        )
        fig_days.update_traces(texttemplate='%{text} зак.', textposition='outside')
        st.plotly_chart(fig_days)

    with st.expander("Детализация по дням недели"):
        st.dataframe(
            df_days,
            hide_index=True,
            column_config={
                "period": "День недели",
                "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
                "order_count": st.column_config.NumberColumn("Кол-во заказов", format="%d")
            }
        )

with tab2:
    with st.container(border=True):
        st.subheader("Выручка по часам суток")

        fig_hours = px.line(
            df_hours,
            x='period',
            y='revenue',
            line_shape='spline',
            labels={'period': 'Час', 'revenue': 'Выручка (₽)'},
            color_discrete_sequence=['#2ca02c']
        )

        fig_hours.update_traces(
            hovertemplate="<b>%{x}</b><br>Выручка: %{y:,.0f} ₽<br>Заказов: %{customdata[0]}<extra></extra>",
            customdata=df_hours[['order_count']].values
        )

        fig_hours.update_layout(
            xaxis_title="Время",
            yaxis_title="Выручка (₽)",
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2
            )
        )

        st.plotly_chart(fig_hours)

    with st.expander("Детализация по часам"):
        st.dataframe(
            df_hours,
            hide_index=True,
            column_config={
                "period": "Время",
                "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
                "order_count": st.column_config.NumberColumn("Кол-во заказов", format="%d")
            }
        )

with tab3:
    with st.container(border=True):
        st.subheader("Динамика выручки по месяцам")
        fig_months = px.area(
            df_months, x='period', y='revenue',
            color='revenue',
            labels={'period': 'Месяц', 'revenue': 'Выручка (₽)'},
            hover_data={'order_count': True}
        )
        st.plotly_chart(fig_months)

    with st.expander("Детализация по месяцам"):
        st.dataframe(
            df_months,
            hide_index=True,
            column_config={
                "period": "Месяц",
                "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
                "order_count": st.column_config.NumberColumn("Кол-во заказов", format="%d")
            }
        )
