import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
import time

def init_auth():
    """Inicializa Firebase Authentication"""
    if not firebase_admin._apps:
        try:
            cred_dict = {
                "type": st.secrets["firebase"]["type"],
                "project_id": st.secrets["firebase"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"],
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error al inicializar Firebase: {str(e)}")
            return False
    return True

def login():
    """Maneja el proceso de login"""
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("Inicio de Sesión")
        
        col1, col2 = st.columns([1,1])
        with col1:
            email = st.text_input("Email")
        with col2:
            password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión", use_container_width=True):
            try:
                # Verificar credenciales contra Firebase
                user = auth.get_user_by_email(email)
                
                # Aquí deberías verificar la contraseña de forma segura
                # Por ahora, usaremos una lista de usuarios autorizados en secrets
                if email in st.secrets["auth"]["authorized_users"]:
                    if password == st.secrets["auth"]["authorized_users"][email]:
                        st.session_state.user = user
                        st.session_state.user_email = email
                        st.success("¡Inicio de sesión exitoso!")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("Contraseña incorrecta")
                else:
                    st.error("Usuario no autorizado")
            except Exception as e:
                st.error("Error en el inicio de sesión. Verifica tus credenciales.")
                st.error(f"Detalles: {str(e)}")

    return st.session_state.user is not None

def logout():
    """Cierra la sesión del usuario"""
    st.session_state.user = None
    st.session_state.user_email = None
    st.success("Sesión cerrada exitosamente")
    time.sleep(1)
    st.experimental_rerun()

def check_session():
    """Verifica si hay una sesión activa"""
    return 'user' in st.session_state and st.session_state.user is not None
