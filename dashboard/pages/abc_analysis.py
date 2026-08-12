import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

auth_guard.require_auth() 
st.set_page_config(layout="wide")
st.title("ABC-анализ ассортимента")

st.markdown("""
**Принцип Парето в действии:**
- 🟢 **Группа A**: ~20% товаров, дающих ~80% выручки (Локомотивы)
- 🟡 **Группа B**: ~30% товаров, дающих ~15% выручки (Середнячки)
- 🔴 **Группа C**: ~50% товаров, дающих ~5% выручки (Аутсайдеры)
""")

@st.cache_data(ttl=600)
def load_abc_analysis_data():
    return api_client.get_abc_analysis()

with st.spinner("Расчет категорий..."):
    try:
        abc_data = load_abc_analysis_data()
        
        if not abc_data:
            st.warning("Нет данных для анализа")
        else:
            df = pd.DataFrame(abc_data)
            
            df_sorted = df.sort_values(by='revenue', ascending=False)
            
            st.subheader("Визуализация вклада товаров")
            fig = px.treemap(
                df,
                path=['category', 'product_name'],
                values='revenue',
                color='category',
                color_discrete_map={
                    'A': '#00CC96',  
                    'B': '#FFA15A', 
                    'C': '#EF553B'  
                },
                custom_data=['cumulative_percent']
            )
            
            fig.update_traces(
                texttemplate="<b>%{label}</b><br>%{value:,.0f} ₽",
                hovertemplate="<b>%{label}</b><br>Выручка: %{value:,.0f} ₽<br>Накопительный %: %{customdata[0]:.1f}%<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Детализация по товарам"):
                st.dataframe(
                    df_sorted[['product_name', 'category', 'revenue', 'cumulative_percent']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
                        "cumulative_percent": st.column_config.NumberColumn("Накоп. %", format="%.1f%%")
                    }
                )
            
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API. Убедитесь, что сервер запущен на порту 8000.")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")