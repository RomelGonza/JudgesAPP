import streamlit as st
import firebase_admin
from firebase_admin import auth
import pyrebase

def init_auth():
    """Inicializa la configuración de Firebase Authentication"""
    firebase_config = {
        "apiKey": st.secrets["firebase"]["api_key"],
        "authDomain": st.secrets["firebase"]["auth_domain"],
        "projectId": st.secrets["firebase"]["project_id"],
        "storageBucket": st.secrets["firebase"]["storage_bucket"],
        "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
        "appId": st.secrets["firebase"]["app_id"],
        "databaseURL": st.secrets["firebase"]["database_url"]
    }
    return pyrebase.initialize_app(firebase_config)

def login():
    """Maneja el proceso de login con Firebase"""
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("Inicio de Sesión")
        
        col1, col2 = st.columns([1,1])
        with col1:
            email = st.text_input("Email")
        with col2:
            password = st.text_input("Contraseña", type="password")

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Iniciar Sesión", use_container_width=True):
                try:
                    firebase = init_auth()
                    auth = firebase.auth()
                    user = auth.sign_in_with_email_and_password(email, password)
                    
                    # Verificar email
                    user_info = auth.get_account_info(user['idToken'])
                    email_verified = user_info['users'][0]['emailVerified']
                    
                    if email_verified:
                        st.session_state.user = user
                        st.session_state.user_email = email
                        st.success("¡Inicio de sesión exitoso!")
                        st.experimental_rerun()
                    else:
                        st.error("Por favor verifica tu email antes de iniciar sesión")
                except Exception as e:
                    st.error("Error en el inicio de sesión. Verifica tus credenciales.")
        
        with col2:
            if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
                if email:
                    try:
                        firebase = init_auth()
                        auth = firebase.auth()
                        auth.send_password_reset_email(email)
                        st.success("Se ha enviado un email para restablecer tu contraseña")
                    except:
                        st.error("Error al enviar el email de recuperación")
                else:
                    st.warning("Por favor ingresa tu email primero")

    return st.session_state.user is not None

def logout():
    """Cierra la sesión del usuario"""
    st.session_state.user = None
    st.session_state.user_email = None
    st.success("Sesión cerrada exitosamente")
    st.experimental_rerun()

def check_session():
    """Verifica si hay una sesión activa"""
    return 'user' in st.session_state and st.session_state.user is not None
