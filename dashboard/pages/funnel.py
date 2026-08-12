import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client

st.set_page_config(layout="wide")
st.title("Воронка конверсии заказов")

st.markdown("""
Показывает, как заказы переходят между статусами. 
*Примечание: из-за особенностей генерации тестовых данных, абсолютное количество 'paid' может превышать 'new'. 
В реальной системе воронка всегда сужается сверху вниз.*
""")

@st.cache_data(ttl=600)
def load_funnel_data():
    return api_client.get_funnel_data()

with st.spinner("Загрузка данных..."):
    try:
        funnel_data = load_funnel_data()
        
        if not funnel_data:
            st.warning("Нет данных для отображения")
        else:
            df = pd.DataFrame(funnel_data)
            
            df = df.sort_values(by='count', ascending=False)
            
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
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Детализация конверсии"):
                st.dataframe(df, use_container_width=True, hide_index=True)
                
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")