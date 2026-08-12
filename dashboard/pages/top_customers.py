import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth(required_role='manager') 
st.set_page_config(
    page_title="Топ покупателей",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Топ клиентов")

st.markdown("Рейтинг покупателей по общей сумме потраченных средств. Основа для программ лояльности и VIP-обслуживания.")

limit = st.slider("Количество клиентов в топе", min_value=10, max_value=100, value=20, step=10)

@st.cache_data(ttl=600)
def load_top_customers_data(limit: int):
    return api_client.get_top_customers_data(limit=limit)

with st.spinner("Загрузка данных..."):
    try:
        customers_data = load_top_customers_data(int(limit))
        
        if not customers_data:
            st.warning("Нет данных о клиентах")
        else:
            df = pd.DataFrame(customers_data)
            
            total_top_revenue = df['total_spent'].sum()
            total_top_orders = df['order_count'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Выручка от топ-клиентов", f"{total_top_revenue:,.0f} ₽")
            col2.metric("Всего заказов от них", f"{total_top_orders:,}")
            
            st.divider()
            
            st.subheader(f"Топ-{limit} клиентов по сумме покупок")
            df_chart = df.head(15) 
            
            fig = px.bar(
                df_chart,
                y='full_name',
                x='total_spent',
                orientation='h',
                color='total_spent',
                color_continuous_scale='Plasma',
                labels={'full_name': 'Клиент', 'total_spent': 'Потрачено (₽)'},
                hover_data={'city': True, 'order_count': True}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Детализация"):
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "full_name": "Имя клиента",
                        "email": "Email",
                        "city": "Город",
                        "total_spent": st.column_config.NumberColumn("Потрачено", format="%.2f ₽"),
                        "order_count": st.column_config.NumberColumn("Заказов", format="%d"),
                        "last_order_date": st.column_config.DateColumn("Последний заказ", format="DD.MM.YYYY")
                    }
                )
            
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")