import streamlit as st
import plotly.express as px
from datetime import date, timedelta
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard


st.set_page_config(
    page_title="Выручка по периодам",
    page_icon="📈"
)
auth_guard.require_auth(required_role='analyst')


@st.cache_data(ttl=60)
def load_revenue_data(start_date: str, end_date: str) -> list[dict]:
    return api_client.get_revenue(
        start_date=start_date,
        end_date=end_date
    )


@st.cache_data(ttl=60)
def load_avg_check_data(start_date: str, end_date: str) -> dict:
    return api_client.get_average_check(
        start_date=start_date,
        end_date=end_date
    )


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("📈 Выручка по периодам")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            st.cache_data.clear()
            st.rerun()

st.markdown("Анализ динамики выручки по дням с фильтрами по датам.")


with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Дата начала",
            value=date.today() - timedelta(days=30),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today(),
            help="Начальная дата периода анализа"
        )
    with col2:
        end_date = st.date_input(
            "Дата окончания",
            value=date.today(),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today(),
            help="Конечная дата периода анализа"
        )


with st.spinner("Загрузка данных из API..."):
    try:
        revenue_data = load_revenue_data(start_date.isoformat(), end_date.isoformat())
        avg_check_data = load_avg_check_data(start_date.isoformat(), end_date.isoformat())
        
        if not revenue_data or not avg_check_data:
            st.warning("Нет данных за выбранный период или доступ ограничен.")
            st.stop()
        
        total_revenue = sum(item['revenue'] for item in revenue_data)
        avg_check = avg_check_data['average_check']
        days_count = len(revenue_data)
        avg_daily_revenue = total_revenue / days_count if days_count > 0 else 0
        
        best_day = max(revenue_data, key=lambda x: x['revenue'])
        worst_day = min(revenue_data, key=lambda x: x['revenue'])
        
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
        st.metric("💰 Общая выручка", f"{total_revenue:,.2f} ₽")
    with col2:
        st.metric("💵 Средний чек", f"{avg_check:,.2f} ₽")
    with col3:
        st.metric("📅 Дней с продажами", days_count)
    with col4:
        st.metric("📊 Среднедневная выручка", f"{avg_daily_revenue:,.2f} ₽")


with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📈 **Лучший день:** {best_day['day']} — выручка **{best_day['revenue']:,.2f} ₽**")
    with col2:
        st.error(f"📉 **Худший день:** {worst_day['day']} — выручка **{worst_day['revenue']:,.2f} ₽**")


with st.container(border=True):
    st.subheader("Динамика выручки по дням")
    fig = px.line(
        revenue_data,
        x='day',
        y='revenue',
        labels={'day': 'Дата', 'revenue': 'Выручка (₽)'},
        markers=True,
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(
        xaxis_title="Дата",
        yaxis_title="Выручка (₽)",
        hovermode='x unified'
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Выручка: %{y:,.2f} ₽<extra></extra>"
    )
    st.plotly_chart(fig)


with st.expander("Детализация"):
    st.dataframe(
        revenue_data,
        hide_index=True,
        column_config={
            "day": st.column_config.DateColumn("Дата", format="DD.MM.YYYY"),
            "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
        }
    )