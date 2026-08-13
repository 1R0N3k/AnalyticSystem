import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services import api_client, auth_guard

st.set_page_config(
    page_title="ABC-анализ ассортимента",
    page_icon="🏷️"
)
auth_guard.require_auth(required_role='manager')


@st.cache_data(ttl=60)
def load_abc_analysis_data() -> list[dict]:
    return api_client.get_abc_analysis()


with st.container(vertical_alignment="center"):
    col_title, col_refresh = st.columns([20, 1], gap="xxlarge")
    with col_title:
        st.title("🏷️ ABC-анализ ассортимента")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/directory_sync:", help="Обновить данные"):
            load_abc_analysis_data.clear()
            st.rerun()


with st.container(border=True):
    st.markdown("""
    **Принцип Парето в действии:**
    - 🟢 **Группа A**: ~20% товаров, дающих ~80% выручки (Локомотивы)
    - 🟡 **Группа B**: ~30% товаров, дающих ~15% выручки (Середнячки)
    - 🔴 **Группа C**: ~50% товаров, дающих ~5% выручки (Аутсайдеры)
    """)


with st.spinner("Расчёт категорий..."):
    try:
        abc_data = load_abc_analysis_data()
        
        if not abc_data:
            st.warning("Нет данных для анализа или доступ ограничен.")
            st.stop()
        
        df = pd.DataFrame(abc_data)
        df_sorted = df.sort_values(by='revenue', ascending=False)
        
        total_products = len(df)
        group_a = df[df['category'] == 'A']
        group_b = df[df['category'] == 'B']
        group_c = df[df['category'] == 'C']
        
        count_a = len(group_a)
        count_b = len(group_b)
        count_c = len(group_c)
        
        revenue_a = group_a['revenue'].sum()
        revenue_b = group_b['revenue'].sum()
        revenue_c = group_c['revenue'].sum()
        
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API.")
        st.stop()
    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")
        st.stop()


with st.container(border=True):
    st.subheader("Распределение товаров по группам")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("**🟢 Группа A**", f"{count_a} товаров")
    with col2:
        st.metric("**🟡 Группа B**", f"{count_b} товаров")
    with col3:
        st.metric("**🔴 Группа C**", f"{count_c} товаров")
    
    st.divider()
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("**Выручка**", f"{revenue_a:,.0f} ₽")
    with col5:
        st.metric("**Выручка**", f"{revenue_b:,.0f} ₽")
    with col6:
        st.metric("**Выручка**", f"{revenue_c:,.0f} ₽")


with st.container(border=True):
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
    st.plotly_chart(fig)


with st.expander("Детализация"):
    st.dataframe(
        df_sorted[['product_name', 'category', 'revenue', 'cumulative_percent']],
        hide_index=True,
        column_config={
            "product_name": st.column_config.TextColumn("Товар", width="large"),
            "category": st.column_config.TextColumn("Группа", width="small"),
            "revenue": st.column_config.NumberColumn("Выручка", format="%.2f ₽"),
            "cumulative_percent": st.column_config.NumberColumn("Накоп. %", format="%.1f%%")
        }
    )