import streamlit as st

pages = [
    st.Page("pages/application.py", title="О системе", icon="📈"),
    st.Page("pages/revenue.py", title="Выручка по периодам", icon="📈"),
    st.Page("pages/top_products.py", title="Топ товаров", icon="🏆"),
    st.Page("pages/customers.py", title="Клиенты по городам", icon="👥"),
    st.Page("pages/margin.py", title="Финансы и Маржинальность", icon="💰"),
    st.Page("pages/abc_analysis.py", title="ABC-анализ", icon="🏷️"),
    st.Page("pages/funnel.py", title="Воронка конверсии", icon="🌪️"),
    st.Page("pages/temporal_analytics.py", title="Временная аналитика", icon="⏰"),
    st.Page("pages/top_customers.py", title="Топ клиентов", icon="👑"),
]

pg = st.navigation(pages)
pg.run()