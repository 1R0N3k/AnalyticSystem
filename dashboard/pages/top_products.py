import streamlit as st
import plotly.express as px
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

st.set_page_config(
    page_title="Топ товаров по выручке",
    page_icon="🏆"
)

auth_guard.require_auth(required_role='analyst')

@st.cache_data(ttl=60)
def load_products_data(limit: int) -> list[dict]:
    return api_client.get_top_products(limit=limit)


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20,1], gap="xxlarge")
    with col_title:
        st.title("🏆 Топ товаров по выручке")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:",  help="Обновить данные"):
            st.cache_data.clear()
            st.rerun()
st.markdown("Рейтинг самых продаваемых товаров с аналитикой по выручке и количеству продаж.")

if "layout_horizontal" not in st.session_state:
    st.session_state.layout_horizontal = False

with st.container(
        border=True, 
        horizontal_alignment="right",
        vertical_alignment="center",        
    ):
    col_slider, col_layout = st.columns([6, 1], gap="small")

    with col_slider:
        limit = st.slider(
            "Количество товаров в топе",
            min_value=5,
            max_value=50,
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
        products_data = load_products_data(int(limit))
        
        if not products_data:
            st.warning("Нет данных о товарах или доступ ограничен.")
            st.stop()
        
        total_revenue = sum(item['total_revenue'] for item in products_data)
        total_quantity = sum(item['total_quantity'] for item in products_data)
        avg_price = total_revenue / total_quantity if total_quantity > 0 else 0
        
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
        st.metric("Выручка топ-товаров", f"{total_revenue:,.2f} ₽")
    with col2:
        st.metric("Продано единиц", f"{total_quantity:,}")
    with col3:
        st.metric("Средняя цена", f"{avg_price:,.2f} ₽")

fig_revenue = px.bar(
    products_data,
    x='total_revenue',
    y='product_name',
    orientation='h',
    labels={'total_revenue': 'Выручка (₽)', 'product_name': 'Товар'},
    color='total_revenue',
    color_continuous_scale='Viridis',
    text='total_revenue'
)
fig_revenue.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    hovermode='y unified',
    margin=dict(l=100, r=50, t=30, b=50),
    yaxis_tickfont=dict(size=10),
)
fig_revenue.update_traces(texttemplate='₽%{text:,.0f}', textposition='outside')

fig_quantity = px.bar(
    products_data,
    x='total_quantity',
    y='product_name',
    orientation='h',
    labels={'total_quantity': 'Количество продаж', 'product_name': 'Товар'},
    color='total_quantity',
    color_continuous_scale='Plasma',
    text='total_quantity'
)
fig_quantity.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    hovermode='y unified',
    margin=dict(l=100, r=50, t=30, b=50),
    yaxis_tickfont=dict(size=10),
)
fig_quantity.update_traces(texttemplate='%{text} шт.', textposition='outside')


if st.session_state.layout_horizontal:
    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            st.subheader("По выручке")
            st.plotly_chart(fig_revenue)
    with col_right:
        with st.container(border=True):
            st.subheader("По количеству")
            st.plotly_chart(fig_quantity)
else:
    with st.container(border=True):
        st.subheader("Топ товаров по выручке")
        st.plotly_chart(fig_revenue)
    
    with st.container(border=True):
        st.subheader("Топ товаров по количеству продаж")
        st.plotly_chart(fig_quantity)


with st.expander("Детализация"):
    st.dataframe(
        products_data,
        
        hide_index=True,
        column_config={
            "product_name": st.column_config.TextColumn("Товар", width="large"),
            "total_revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
            "total_quantity": st.column_config.NumberColumn("Продано, шт.", format="%d"),
        }
    )