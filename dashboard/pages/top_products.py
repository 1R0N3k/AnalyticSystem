import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client

st.title("Топ товаров по выручке")

limit = st.slider(
    "Количество товаров в топе",
    min_value=5,
    max_value=25,
    value=10,
    step=5
)

if st.button("Загрузить данные", type="primary"):
    with st.spinner("Загрузка данных из API..."):
        try:
            products_data = api_client.get_top_products(limit=limit)
            
            if not products_data:
                st.warning("Нет данных о товарах")
            else:
                total_revenue = sum(item['total_revenue'] for item in products_data)
                total_quantity = sum(item['total_quantity'] for item in products_data)
                
                st.subheader("Ключевые показатели")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Выручка топ-товаров", f"{total_revenue:,.2f} ₽")
                with col2:
                    st.metric("Продано единиц", total_quantity)
                
                st.subheader("Рейтинг товаров")
                fig = px.bar(
                    products_data,
                    x='total_revenue',
                    y='product_name',
                    orientation='h',
                    title=f'Топ-{limit} товаров по выручке',
                    labels={
                        'total_revenue': 'Выручка (₽)',
                        'product_name': 'Товар'
                    },
                    color='total_revenue',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    hovermode='y unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Детализация")
                st.dataframe(products_data, use_container_width=True)
                
        except requests.exceptions.ConnectionError:
            st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
        except Exception as e:
            st.error(f"Ошибка при загрузке данных: {e}")

else:
    st.info("Выберите количество товаров и нажмите 'Загрузить данные'")