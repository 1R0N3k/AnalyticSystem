import streamlit as st
import plotly.express as px
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, download_converter


st.set_page_config(layout="wide")
st.title("Клиенты по городам")

@st.cache_data(ttl=600)
def load_cities_data() -> list[dict]:
    return api_client.get_customers_by_city()

if 'customers_chart_png_data' not in st.session_state:
    st.session_state['customers_chart_png_data'] = None
if 'customers_bar_png_data' not in st.session_state:
    st.session_state['customers_bar_png_data'] = None

with st.spinner("Загрузка данных из API..."):
    try:
        cities_data = load_cities_data()
        
        if not cities_data:
            st.warning("️Нет данных о клиентах")
        else:
            total_cities = len(cities_data)
            total_customers = sum(item['total_customers'] for item in cities_data)
            total_orders = sum(item['total_orders'] for item in cities_data)
            
            st.subheader("Ключевые показатели")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Городов", total_cities)
            with col2:
                st.metric("Всего клиентов", f"{total_customers:,}")
            with col3:
                st.metric("Всего заказов", f"{total_orders:,}")
            
            st.subheader("Распределение заказов по городам")
            
            fig_pie = px.pie(
                cities_data,
                values='total_orders',
                names='city',
                title='Доля заказов по городам',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
        
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
            with st.container(horizontal=True, vertical_alignment="center"):
                if st.session_state.customers_chart_png_data is None:
                    if st.button(
                        "Подготовить график к скачиванию", 
                        key="chart_prepare", 
                        disabled=False if st.session_state.customers_chart_png_data is None else True
                    ):
                        with st.spinner("Генерируем изображение..."):
                            st.session_state.customers_chart_png_data = fig_pie.to_image(format="png")
                            st.rerun()

                if st.session_state.customers_chart_png_data is not None:
                    st.download_button(
                            label="Скачать как PNG",
                            key="png_chart_download",
                            data=st.session_state.customers_chart_png_data,
                            file_name="by_city_chart.png",
                            mime="image/png",
                            on_click="ignore",
                    )

            st.subheader("️ Топ-10 городов по заказам")
            top_10_cities = cities_data[:10]
            fig_bar = px.bar(
                top_10_cities,
                x='city',
                y='total_orders',
                title='Топ-10 городов по количеству заказов',
                labels={
                    'city': 'Город',
                    'total_orders': 'Количество заказов'
                },
                color='total_orders',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            with st.container(horizontal=True, vertical_alignment="center"):
                if st.session_state.customers_bar_png_data is None:
                    if st.button(
                        "Подготовить график к скачиванию", 
                        key="bar_prepare", 
                        disabled=False if st.session_state.customers_bar_png_data is None else True
                    ):
                        with st.spinner("Генерируем изображение..."):
                            st.session_state.customers_bar_png_data = fig_bar.to_image(format="png")
                            st.rerun()

                if st.session_state.customers_bar_png_data is not None:
                    st.download_button(
                            label="Скачать как PNG",
                            key="png_bar_download",
                            data=st.session_state.customers_bar_png_data,
                            file_name="by_city_chart.png",
                            mime="image/png",
                            on_click="ignore",
                    )

            with st.expander("Детализация по городам"):
                st.dataframe(cities_data, use_container_width=True)

                st.download_button(
                    label="Скачать CSV",
                    data=download_converter.convert_for_download_csv(cities_data),
                    file_name="data.csv",
                    mime="text/csv",
                    icon=":material/download:",
                )
            
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")