import streamlit as st
import time

def check_password():
    """Returns `True` if the user had a correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        try:
            authorized_users = st.secrets["auth"]["authorized_users"]
            if (
                st.session_state["username"] in authorized_users
                and st.session_state["password"] == authorized_users[st.session_state["username"]]
            ):
                st.session_state["password_correct"] = True
                st.session_state["current_user"] = st.session_state["username"]
                st.session_state["login_time"] = time.time()
                del st.session_state["password"]
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        except Exception as e:
            st.error(f"Error de autenticación: {str(e)}")
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.error("😕 Usuario o contraseña incorrectos")
        st.button("Entrar", on_click=password_entered)
        return False
    else:
        return True

def check_session_timeout(timeout_seconds=3600):
    """Verifica si la sesión ha expirado"""
    if "login_time" not in st.session_state:
        return False
    
    if time.time() - st.session_state.login_time > timeout_seconds:
        st.session_state.clear()
        st.error("Sesión expirada. Por favor, inicie sesión nuevamente.")
        return False
    return True
