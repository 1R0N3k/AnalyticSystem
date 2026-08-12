import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth() 
st.set_page_config(layout="wide")
st.title("Временная аналитика продаж")

st.markdown("Анализ паттернов покупок: какие дни, часы и месяцы приносят больше всего выручки.")

@st.cache_data(ttl=600)
def load_revenue_by_day_of_week_data() -> list[dict]:
    return api_client.get_revenue_by_day_of_week()

@st.cache_data(ttl=600)
def load_revenue_by_hours_data() -> list[dict]:
    return api_client.get_revenue_by_hour()

@st.cache_data(ttl=600)
def load_revenue_by_month() -> list[dict]:
    return api_client.get_revenue_by_month()

with st.spinner("Загрузка данных..."):
    try:
        days_data = load_revenue_by_day_of_week_data()
        hours_data = load_revenue_by_hours_data()
        months_data = load_revenue_by_month()
        
        if not days_data or not hours_data or not months_data:
            st.warning("Нет данных для отображения")
        else:
            df_days = pd.DataFrame(days_data)
            df_hours = pd.DataFrame(hours_data)
            df_months = pd.DataFrame(months_data)
            
            tab1, tab2, tab3 = st.tabs(["📅 По дням недели", "🕒 По часам", "🗓️ По месяцам"])
            
            with tab1:
                st.subheader("Выручка по дням недели")
                fig_days = px.bar(
                    df_days, x='period', y='revenue', 
                    color='revenue',
                    labels={'period': 'День недели', 'revenue': 'Выручка (₽)'},
                    text='order_count'
                )
                fig_days.update_traces(texttemplate='%{text} зак.', textposition='outside')
                st.plotly_chart(fig_days, use_container_width=True)
                
            with tab2:
                st.subheader("Выручка по часам суток")
                
                fig_hours = px.line(
                    df_hours, 
                    x='period', 
                    y='revenue',
                    line_shape='spline',
                    labels={'period': 'Час', 'revenue': 'Выручка (₽)'},
                    color_discrete_sequence=['#2ca02c']
                )
                
                fig_hours.update_traces(
                    hovertemplate="<b>%{x}</b><br>Выручка: %{y:,.0f} ₽<br>Заказов: %{customdata[0]}<extra></extra>",
                    customdata=df_hours[['order_count']].values
                )
                
                fig_hours.update_layout(
                    xaxis_title="Время",
                    yaxis_title="Выручка (₽)",
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=2
                    )
                )
                
                st.plotly_chart(fig_hours, use_container_width=True)
                
            with tab3:
                st.subheader("Динамика выручки по месяцам")
                fig_months = px.area(
                    df_months, x='period', y='revenue',
                    color='revenue', 
                    labels={'period': 'Месяц', 'revenue': 'Выручка (₽)'},
                    hover_data={'order_count': True}
                )
                st.plotly_chart(fig_months, use_container_width=True)
                
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")