import os
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

st.set_page_config(
    page_title="Топ клиентов",
    page_icon="👑"
)

auth_guard.require_auth(required_role='manager')

@st.cache_data(ttl=60)
def load_top_customers_data(limit: int) -> list[dict]:
    return api_client.get_top_customers_data(limit=limit)


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("👑 Топ клиентов")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            st.cache_data.clear()
            st.rerun()

st.markdown("Рейтинг покупателей по общей сумме потраченных средств. Основа для программ лояльности и VIP-обслуживания.")


with st.container(
    border=True,
    horizontal_alignment="right",
    vertical_alignment="center",
):
    limit = st.slider(
        "Количество клиентов в топе",
        min_value=5,
        max_value=50,
        value=20,
        step=5
    )


with st.spinner("Загрузка данных из API..."):
    try:
        customers_data = load_top_customers_data(int(limit))

        if not customers_data:
            st.warning("Нет данных о клиентах или доступ ограничен.")
            st.stop()

        df = pd.DataFrame(customers_data)

        total_top_revenue = df['total_spent'].sum()
        total_top_orders = df['order_count'].sum()
        avg_client_spent = total_top_revenue / len(df) if len(df) > 0 else 0
        avg_order_value = total_top_revenue / total_top_orders if total_top_orders > 0 else 0

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
        st.metric("💰 Выручка от топ-клиентов", f"{total_top_revenue:,.0f} ₽")
    with col2:
        st.metric("🛒 Всего заказов", f"{total_top_orders:,}")
    with col3:
        st.metric("💵 Средний чек клиента", f"{avg_client_spent:,.0f} ₽")
    with col4:
        st.metric("📊 Средний чек заказа", f"{avg_order_value:,.0f} ₽")


chart_height = 800 if len(df) > 20 else len(df) * 40 + 200


with st.container(border=True):
    st.subheader(f"Топ-{limit} клиентов по сумме покупок")

    fig = px.bar(
        df,
        y='full_name',
        x='total_spent',
        orientation='h',
        color='total_spent',
        color_continuous_scale='Plasma',
        labels={'full_name': 'Клиент', 'total_spent': 'Потрачено (₽)'},
        hover_data={'city': True, 'order_count': True, 'email': True}
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=chart_height,
        margin=dict(l=100, r=50, t=30, b=50),
        yaxis_tickfont=dict(size=10)
    )
    st.plotly_chart(fig)


with st.expander("Детализация"):
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "full_name": st.column_config.TextColumn("Имя клиента", width="medium"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "city": st.column_config.TextColumn("Город", width="small"),
            "total_spent": st.column_config.NumberColumn("Потрачено", format="%.2f ₽"),
            "order_count": st.column_config.NumberColumn("Заказов", format="%d"),
            "last_order_date": st.column_config.DateColumn("Последний заказ", format="DD.MM.YYYY")
        }
    )
