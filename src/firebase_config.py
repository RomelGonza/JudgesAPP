import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

def init_firebase():
    """Inicializa la conexión con Firebase"""
    if not firebase_admin._apps:
        cert_dict = json.loads(st.secrets["firebase"]["cert_json"])
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def get_max_score(criterio, categoria):
    """Obtiene el puntaje máximo según criterio y categoría"""
    limites = {
        "PRESENTACION Y VESTIMENTA": {
            "SIKURIS DE UN SOLO BOMBO": 20,
            "SIKURIS VARIOS BOMBOS": 20,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 20,
            "default": 20
        },
        "MUSICA": {
            "SIKURIS DE UN SOLO BOMBO": 30,
            "SIKURIS VARIOS BOMBOS": 30,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 30,
            "default": 20
        },
        "COREOGRAFIA": {
            "SIKURIS DE UN SOLO BOMBO": 20,
            "SIKURIS VARIOS BOMBOS": 20,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 20,
            "default": 30
        },
        "MUSICA(danzarines y musicos)": {"default": 10},
        "VESTIMENTA(danzarines y musicos)": {"default": 10},
        "RECORRIDO(desplazamiento)": {"default": 7},
        "Brigada Ecologica": {"default": 3},
    }
    criterio_limits = limites.get(criterio, {"default": 30})
    return criterio_limits.get(categoria.upper(), criterio_limits["default"])
