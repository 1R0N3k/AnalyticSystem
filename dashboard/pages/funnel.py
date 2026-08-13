import os
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth(required_role='analyst')
st.set_page_config(
    page_title="Воронка конверсии",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=60)
def load_funnel_data() -> list[dict]:
    return api_client.get_funnel_data()


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("🌪️ Воронка конверсии заказов")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            st.cache_data.clear()
            st.rerun()

st.markdown("""
Показывает, как заказы переходят между статусами.
*Примечание: из-за особенностей генерации тестовых данных, абсолютное количество 'paid' может превышать 'new'.
В реальной системе воронка всегда сужается сверху вниз.*
""")


with st.spinner("Загрузка данных из API..."):
    try:
        funnel_data = load_funnel_data()

        if not funnel_data:
            st.warning("Нет данных для отображения или доступ ограничен.")
            st.stop()

        df = pd.DataFrame(funnel_data)
        df = df.sort_values(by='count', ascending=False)

        total_orders = df['count'].sum()
        new_count = df[df['status_key'] == 'new']['count'].sum() if 'new' in df['status_key'].values else 0
        delivered_count = df[df['status_key'] == 'delivered']['count'].sum() if 'delivered' in df['status_key'].values else 0
        cancelled_count = df[df['status_key'] == 'cancelled']['count'].sum() if 'cancelled' in df['status_key'].values else 0

        conversion_rate = (delivered_count / new_count * 100) if new_count > 0 else 0
        cancellation_rate = (cancelled_count / total_orders * 100) if total_orders > 0 else 0

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
        st.metric("📦 Всего заказов", f"{total_orders:,}")
    with col2:
        st.metric("✅ Доставлено", f"{delivered_count:,}")
    with col3:
        st.metric("📈 Конверсия", f"{conversion_rate:.1f}%")
    with col4:
        st.metric("❌ Отменено", f"{cancelled_count:,} ({cancellation_rate:.1f}%)")


with st.container(border=True):
    st.subheader("Распределение заказов по статусам")
    fig = px.funnel(
        df,
        x='count',
        y='status_name',
        color='status_key',
        color_discrete_map={
            'new': '#636EFA',
            'paid': '#00CC96',
            'delivered': '#AB63FA',
            'cancelled': '#EF553B'
        },
        labels={'count': 'Количество заказов', 'status_name': 'Этап'}
    )

    fig.update_traces(
        textinfo="value+percent initial",
        hovertemplate="<b>%{y}</b><br>Заказов: %{x}<br>Доля: %{text}<extra></extra>"
    )

    st.plotly_chart(fig)


with st.expander("Детализация"):
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "status_name": st.column_config.TextColumn("Статус", width="medium"),
            "status_key": st.column_config.TextColumn("Ключ", width="small"),
            "count": st.column_config.NumberColumn("Количество заказов", format="%d"),
        }
    )
