import streamlit as st
import plotly.express as px
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, download_converter

st.set_page_config(layout="wide")
st.title("Топ товаров по выручке")

if 'top_products_chart_png_data' not in st.session_state:
    st.session_state['top_products_chart_png_data'] = None
if 'last_chart_limit' not in st.session_state:
    st.session_state['last_chart_limit'] = None

@st.cache_data(ttl=600)
def load_products_data(limit: int) -> list[dict]:
    return api_client.get_top_products(limit=limit)

with st.container(border=True):
    limit = st.slider(
        "Количество товаров в топе",
        min_value=5,
        max_value=25,
        value=10,
        step=5
    )

with st.spinner("Загрузка данных из API..."):
    try:
        products_data = load_products_data(limit)
        
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
            
            if st.session_state.last_chart_limit != limit:
                st.session_state.top_products_chart_png_data = None
                st.session_state.last_chart_limit = limit

            with st.container(horizontal=True, vertical_alignment="center"):
                if st.session_state.top_products_chart_png_data is None:
                    if st.button(
                        "Подготовить график к скачиванию", 
                        key="chart_prepare", 
                        disabled=False if st.session_state.top_products_chart_png_data is None else True
                    ):
                        with st.spinner("Генерируем изображение..."):
                            st.session_state.top_products_chart_png_data = fig.to_image(format="png")
                            st.rerun()

                if st.session_state.top_products_chart_png_data is not None:
                    st.download_button(
                            label="Скачать как PNG",
                            data=st.session_state.top_products_chart_png_data,
                            file_name="top_products_chart.png",
                            mime="image/png",
                            on_click="ignore",
                    )

            with st.expander("Детализация"):
                st.dataframe(products_data, use_container_width=True)


                st.download_button(
                        label="Download CSV",
                        data=download_converter.convert_for_download_csv(products_data),
                        file_name="data.csv",
                        mime="text/csv",
                        icon=":material/download:",
                )
            
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")