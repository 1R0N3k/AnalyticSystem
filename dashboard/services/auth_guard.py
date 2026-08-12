import streamlit as st
from . import api_client

def require_auth(required_role: str = None):
    if "auth_token" not in st.session_state:
        st.set_page_config(page_title="Авторизация", layout="centered")
        st.title("Авторизация в системе")
        st.markdown("Пожалуйста, войдите в систему для доступа к аналитическому дашборду.")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Логин", placeholder="Например: testuser")
            password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
            submitted = st.form_submit_button("Войти", type="primary", use_container_width=True)
            
            if submitted:
                if username and password:
                    success = api_client.login_user(username, password)
                    if success:
                        st.rerun()
                else:
                    st.warning("Введите логин и пароль")
        
        st.stop()

    if required_role:
        user_roles = st.session_state.get("roles", [])
        if required_role not in user_roles:
            st.set_page_config(page_title="Доступ запрещён", layout="centered")
            st.error("**Доступ запрещён**")
            st.info(f"Для просмотра этой страницы требуется роль: **{required_role}**.\nВаши текущие роли: `{', '.join(user_roles) if user_roles else 'нет'}`")
            
            if st.button("Выйти из системы", type="secondary"):
                api_client.logout_user()
            st.stop()

    with st.sidebar:
        st.markdown("---")
        st.write(f"Пользователь: **{st.session_state.username}**")
        st.write(f"Роль: `{', '.join(st.session_state.roles)}`")
        if st.button("Выйти", use_container_width=True, type="secondary"):
            api_client.logout_user()