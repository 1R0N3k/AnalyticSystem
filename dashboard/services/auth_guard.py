import requests
import streamlit as st

from . import api_client

ROLE_LEVELS = {
    'analyst': 1,
    'manager': 2,
}

def require_auth(required_role: str = None):
    try:
        if "auth_token" not in st.session_state:
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

        with st.sidebar:
            st.write(f"Пользователь: **{st.session_state.username}**")
            roles_text = ", ".join(st.session_state.roles) if st.session_state.roles else "нет"
            st.write(f"Роли: `{roles_text}`")
            if st.button("Выйти", use_container_width=True, type="secondary"):
                api_client.logout_user()

        if required_role:
            user_roles = st.session_state.get("roles", [])

            required_level = ROLE_LEVELS.get(required_role, 99)

            user_max_level = max([ROLE_LEVELS.get(role, 0) for role in user_roles], default=0)

            if user_max_level < required_level:
                st.error("**Доступ запрещён**")
                st.info(
                    f"Для просмотра этой страницы требуется уровень доступа: **{required_role}** (Уровень {required_level}).\n\n"
                    f"Ваши текущие роли: **{', '.join(user_roles) if user_roles else 'нет'}** (Макс. уровень: {user_max_level})\n\n"
                    f"Вы можете перейти на другую страницу через меню слева."
                )
                st.stop()
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к Django API.")
        st.stop()
    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")
        st.stop()
