import streamlit as st
import plotly.express as px
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard


auth_guard.require_auth(required_role='analyst')


@st.cache_data(ttl=60)
def load_cities_data() -> list[dict]:
    return api_client.get_customers_by_city()


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("👥 Клиенты по городам")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            load_cities_data.clear()
            st.rerun()

st.markdown("Географическое распределение заказов и клиентов.")


if "layout_horizontal" not in st.session_state:
    st.session_state.layout_horizontal = False

with st.container(
    border=True,
    horizontal_alignment="right",
    vertical_alignment="center",
):
    col_slider, col_layout = st.columns([6, 1], gap="small")

    with col_slider:
        top_n = st.slider(
            "Количество городов в рейтинге",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )

    with col_layout:
        st.markdown("<br>", unsafe_allow_html=True)
        st.session_state.layout_horizontal = st.toggle(
            "Блочное расположение",
            value=st.session_state.layout_horizontal
        )


with st.spinner("Загрузка данных из API..."):
    try:
        cities_data = load_cities_data()
        
        if not cities_data:
            st.warning("Нет данных о клиентах или доступ ограничен.")
            st.stop()
        
        total_cities = len(cities_data)
        total_customers = sum(item['total_customers'] for item in cities_data)
        total_orders = sum(item['total_orders'] for item in cities_data)
        
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API.")
        st.stop()
    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")
        st.stop()


with st.container(border=True):
    st.subheader("Ключевые показатели")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Городов", total_cities)
    with col2:
        st.metric("Всего клиентов", f"{total_customers:,}")
    with col3:
        st.metric("Всего заказов", f"{total_orders:,}")


top_cities = cities_data[:top_n]

fig_pie = px.pie(
    cities_data,
    values='total_orders',
    names='city',
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

fig_bar = px.bar(
    top_cities,
    x='city',
    y='total_orders',
    labels={
        'city': 'Город',
        'total_orders': 'Количество заказов'
    },
    color='total_orders',
    color_continuous_scale='Blues',
    text='total_orders'
)
fig_bar.update_layout(
    xaxis_tickangle=-45,
)
fig_bar.update_traces(texttemplate='%{text}', textposition='outside')


if st.session_state.layout_horizontal:
    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            st.subheader("Доля заказов по городам")
            st.plotly_chart(fig_pie)
    with col_right:
        with st.container(border=True):
            st.subheader(f"Топ-{top_n} городов по заказам")
            st.plotly_chart(fig_bar)
else:
    with st.container(border=True):
        st.subheader("Доля заказов по городам")
        st.plotly_chart(fig_pie)
    
    with st.container(border=True):
        st.subheader(f"Топ-{top_n} городов по заказам")
        st.plotly_chart(fig_bar)


with st.expander("Детализация"):
    st.dataframe(
        cities_data,
        hide_index=True,
        column_config={
            "city": st.column_config.TextColumn("Город", width="large"),
            "total_customers": st.column_config.NumberColumn("Клиентов", format="%d"),
            "total_orders": st.column_config.NumberColumn("Заказов", format="%d"),
        }
    )