
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Inicializar Firebase solo si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("trabajo-ad596-firebase-adminsdk-fbsvc-8c2bebdfe5.json")
    firebase_admin.initialize_app(cred)

# Obtener referencia a la base de datos de Firestore
db = firestore.client()

def get_max_score(criterio, categoria):
    # Mantener la misma lógica de límites máximos
    limites = {
        "PRESENTACION Y VESTIMENTA": {
            "SIKURIS DE UN SOLO BOMBO": 20,
            "SIKURIS VARIOS BOMBOS": 20,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 20,
            "default": 20
        },
        # ... resto de los límites ...
    }
    criterio_limits = limites.get(criterio, {"default": 30})
    return criterio_limits.get(categoria.upper(), criterio_limits["default"])

def cargar_candidatos():
    try:
        candidatos_ref = db.collection("Agrupaciones_dia1").order_by("numero").stream()
        return [(c.id, f"{c.to_dict()['nombre_del_conjunto']} (N° {c.to_dict()['numero']})") 
                for c in candidatos_ref]
    except Exception as e:
        st.error(f"Error al cargar candidatos: {e}")
        return []

def main():
    st.title("Candelaria Originarios")
    
    # Simulación de login (reemplazar con tu sistema de autenticación)
    email = "jurado01@gmail.com"  # Ejemplo
    
    # Cargar candidatos
    candidatos = cargar_candidatos()
    
    # Dropdown para seleccionar candidato
    candidato_seleccionado = st.selectbox(
        "Seleccione un conjunto",
        options=[c[0] for c in candidatos],
        format_func=lambda x: dict(candidatos)[x]
    )
    
    if candidato_seleccionado:
        candidato_doc = db.collection("Agrupaciones_dia1").document(candidato_seleccionado).get()
        if candidato_doc.exists:
            datos = candidato_doc.to_dict()
            
            # Mostrar información del conjunto
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"### N° {datos['numero']}")
            with col2:
                st.markdown(f"**Conjunto:** {datos['nombre_del_conjunto']}")
                st.markdown(f"**Categoría:** {datos['categoria']}")
            
            # Campo de calificación
            calificacion = st.number_input(
                "Calificación",
                min_value=0.0,
                max_value=get_max_score(obtener_criterio_calificacion(obtener_numero_jurado()), datos['categoria']),
                step=1.0
            )
            
            if st.button("Enviar Calificación"):
                # Aquí iría la lógica de envío
                pass

if __name__ == "__main__":
    main()
