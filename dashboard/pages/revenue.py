import streamlit as st
import plotly.express as px
from datetime import date, timedelta
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, download_converter

st.set_page_config(layout="wide")
st.title("Выручка по периодам")
    
if 'revenue_chart_png_data' not in st.session_state:
    st.session_state['revenue_chart_png_data'] = None
if 'last_chart_dates' not in st.session_state:
    st.session_state['last_chart_dates'] = None

@st.cache_data(ttl=600)
def load_revenue_data(start_date: st.date_input, end_date: st.date_input) -> list[dict]:
    return api_client.get_revenue(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

@st.cache_data(ttl=600)
def load_avg_check_data(start_date: st.date_input, end_date: st.date_input) -> list[dict]:
    return api_client.get_average_check(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

def update_chart_png_data():
    st.session_state.revenue_chart_png_data = None

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Дата начала",
            value=date.today() - timedelta(days=30),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today()
        )    
    with col2:
        end_date = st.date_input(
            "Дата окончания",
            value=date.today(),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today()            
        )

with st.spinner("Загрузка данных из API..."):
    try:
        revenue_data = load_revenue_data(start_date, end_date)
        avg_check_data = load_avg_check_data(start_date, end_date)
        
        if not revenue_data:
            st.warning("Нет данных за выбранный период")
        else:
            total_revenue = sum(item['revenue'] for item in revenue_data)
            avg_check = avg_check_data['average_check']
            days_count = len(revenue_data)
            
            st.subheader("Ключевые показатели")
            col1, col2, col3 = st.columns(3, gap="large")
            with col1:
                st.metric("Общая выручка", f"{total_revenue:,.2f} ₽")
            with col2:
                st.metric("Средний чек", f"{avg_check:,.2f} ₽")
            with col3:
                st.metric("Дней с продажами", days_count)

            st.subheader("Динамика выручки")
            fig = px.line(
                revenue_data,
                x='day',
                y='revenue',
                title='Выручка по дням',
                labels={'day': 'Дата', 'revenue': 'Выручка (₽)'},
                markers=True
            )
            fig.update_layout(
                xaxis_title="Дата",
                yaxis_title="Выручка (₽)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            current_dates = (start_date, end_date)
            if st.session_state.last_chart_dates != current_dates:
                st.session_state.revenue_chart_png_data = None
                st.session_state.last_chart_dates = current_dates

            with st.container(horizontal=True, vertical_alignment="center"):
                if st.session_state.revenue_chart_png_data is None:
                    if st.button(
                        "Подготовить график к скачиванию", 
                        key="chart_prepare", 
                        disabled=False if st.session_state.revenue_chart_png_data is None else True
                    ):
                        with st.spinner("Генерируем изображение..."):
                            st.session_state.revenue_chart_png_data = fig.to_image(format="png")
                            st.rerun()

                if st.session_state.revenue_chart_png_data is not None:
                    st.download_button(
                            label="Скачать как PNG",
                            data=st.session_state.revenue_chart_png_data,
                            file_name="by_day_revenue_chart.png",
                            mime="image/png",
                            on_click="ignore",
                    )
            
            with st.expander("Детализация по дням"):
                st.dataframe(revenue_data, use_container_width=True)

                st.download_button(
                        label="Download CSV",
                        data=download_converter.convert_for_download_csv(revenue_data),
                        file_name="data.csv",
                        mime="text/csv",
                        icon=":material/download:",
                )

    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")