import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Configuración de la página
st.set_page_config(
    page_title="Candelaria Originarios",
    layout="wide"
)

# Inicializar Firebase solo si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("trabajo-ad596-firebase-adminsdk-fbsvc-8c2bebdfe5.json")
    firebase_admin.initialize_app(cred)

# Obtener referencia a la base de datos de Firestore
db = firestore.client()

# Funciones auxiliares
def get_max_score(criterio, categoria):
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

def obtener_numero_jurado(email):
    jurados = {
        "jurado1@gmail.com": 1,
        "jurado2@gmail.com": 2,
        "jurado3@gmail.com": 3,
        "jurado4@gmail.com": 4,
        "jurado5@gmail.com": 5,
        "jurado6@gmail.com": 6,
        "jurado7@gmail.com": 7,
        "jurado8@gmail.com": 8,
        "jurado9@gmail.com": 9,
        "jurado01@gmail.com": 10,
        "jurado02@gmail.com": 11,
        "jurado03@gmail.com": 12,
        "jurado04@gmail.com": 13,
    }
    return jurados.get(email, 0)

def obtener_criterio_calificacion(jurado_num):
    criterios_jurados = {
        (1, 2, 3): "PRESENTACION Y VESTIMENTA",
        (4, 5, 6): "MUSICA",
        (7, 8, 9): "COREOGRAFIA",
        (10,): "MUSICA(danzarines y musicos)",
        (11,): "VESTIMENTA(danzarines y musicos)",
        (12,): "RECORRIDO(desplazamiento)",
        (13,): "Brigada Ecologica",
    }
    for jurados, criterio in criterios_jurados.items():
        if jurado_num in jurados:
            return criterio
    return "CRITERIO NO ASIGNADO"

def obtener_campo_firebase(jurado_num, categoria):
    campos_etapa1 = {
        (1, 2, 3): "e_calificacion_jurado{}_pv",
        (4, 5, 6): "e_calificacion_jurado{}_mc",
        (7, 8, 9): "e_calificacion_jurado{}_c",
        (10,): "v_calificacion_jurado_mc",
        (11,): "v_calificacion_jurado_v",
        (12,): "v_calificacion_jurado_pdl",
        (13,): "v_calificacion_jurado_ci"
    }
    for jurados, campo in campos_etapa1.items():
        if jurado_num in jurados:
            return campo.format(jurado_num)
    return None

def cargar_candidatos():
    try:
        candidatos_ref = db.collection("Agrupaciones_dia1").order_by("numero").stream()
        return [(c.id, f"{c.to_dict()['nombre_del_conjunto']} (N° {c.to_dict()['numero']})") 
                for c in candidatos_ref]
    except Exception as e:
        st.error(f"Error al cargar candidatos: {e}")
        return []

def actualizar_calificacion(candidato_id, jurado_num, calificaciones, categoria):
    try:
        candidato_ref = db.collection("Agrupaciones_dia1").document(candidato_id)

        if jurado_num in [10, 11, 12, 13]:
            total_score = sum(calificaciones)
            field_mapping = {
                10: "v_calificacion_jurado_mc",
                11: "v_calificacion_jurado_v",
                12: "v_calificacion_jurado_pdl",
                13: "v_calificacion_jurado_ci"
            }
            campo_firebase = field_mapping[jurado_num]
            update_data = {campo_firebase: total_score}
        else:
            campo_firebase = obtener_campo_firebase(jurado_num, categoria)
            update_data = {campo_firebase: calificaciones[0]}

        candidato_ref.update(update_data)
        return True, campo_firebase, update_data[campo_firebase]
    except Exception as e:
        st.error(f"Error al actualizar calificación: {e}")
        return False, None, None

def main():
    st.title("Candelaria Originarios")

    # Simulación de login (reemplazar con tu sistema de autenticación)
    email = st.sidebar.text_input("Email del jurado", value="jurado01@gmail.com")
    jurado_num = obtener_numero_jurado(email)
    criterio = obtener_criterio_calificacion(jurado_num)

    st.sidebar.write(f"Criterio de calificación: {criterio}")

    # Cargar y mostrar candidatos
    candidatos = cargar_candidatos()
    candidato_seleccionado = st.selectbox(
        "Seleccione un conjunto",
        options=[c[0] for c in candidatos],
        format_func=lambda x: dict(candidatos)[x] if x else "Seleccione un conjunto"
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

            # Verificar si ya existe calificación
            campo_firebase = obtener_campo_firebase(jurado_num, datos['categoria'])
            if campo_firebase and datos.get(campo_firebase, 0) != 0:
                st.warning("Ya ha calificado a este conjunto.")
                return

            # Sistema de calificación
            if jurado_num in [10, 11, 12, 13]:
                calificaciones = []
                criterios = ["MUSICA", "VESTIMENTA", "RECORRIDO", "Brigada Ecologica"]
                for criterio in criterios:
                    cal = st.number_input(
                        f"Calificación - {criterio}",
                        min_value=0.0,
                        max_value=10.0,
                        step=0.5,
                        key=f"cal_{criterio}"
                    )
                    calificaciones.append(cal)
            else:
                max_valor = get_max_score(criterio, datos['categoria'])
                calificacion = st.number_input(
                    f"Calificación - {criterio}",
                    min_value=0.0,
                    max_value=float(max_valor),
                    step=0.5
                )
                calificaciones = [calificacion]

            # Botón de envío
            if st.button("Enviar Calificación"):
                if st.session_state.get('confirmacion', False):
                    exito, campo, valor = actualizar_calificacion(
                        candidato_seleccionado,
                        jurado_num,
                        calificaciones,
                        datos['categoria']
                    )
                    if exito:
                        st.success("Calificación enviada correctamente")
                        st.session_state.confirmacion = False
                        time.sleep(2)
                        st.experimental_rerun()
                else:
                    st.session_state.confirmacion = True
                    st.warning("¿Está seguro de enviar esta calificación? Presione nuevamente para confirmar.")

if __name__ == "__main__":
    main()
