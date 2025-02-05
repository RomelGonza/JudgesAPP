import streamlit as st
from src.auth import check_password, check_session_timeout
from src.firebase_config import init_firebase, get_max_score
from src.utils import (
    obtener_numero_jurado,
    obtener_criterio_calificacion,
    obtener_campo_firebase
)

def cargar_candidatos(db):
    """Carga los candidatos desde Firebase"""
    try:
        candidatos_ref = db.collection("Agrupaciones_dia1").order_by("numero").stream()
        return [(c.id, f"{c.to_dict()['nombre_del_conjunto']} (N° {c.to_dict()['numero']})") 
                for c in candidatos_ref]
    except Exception as e:
        st.error(f"Error al cargar candidatos: {e}")
        return []

def main():
    st.set_page_config(
        page_title="Candelaria Originarios",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Verificar autenticación y tiempo de sesión
    if not check_password() or not check_session_timeout():
        return

    st.title("Candelaria Originarios")

    # Obtener email del usuario y número de jurado
    email = st.session_state.get("current_user")
    jurado_num = obtener_numero_jurado(email)
    criterio = obtener_criterio_calificacion(jurado_num)

    st.sidebar.write(f"Criterio de calificación: {criterio}")

    # Inicializar Firebase
    db = init_firebase()

    # Cargar y mostrar candidatos
    candidatos = cargar_candidatos(db)
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
                    try:
                        if jurado_num in [10, 11, 12, 13]:
                            total_score = sum(calificaciones)
                            field_mapping = {
                                10: "v_calificacion_jurado_mc",
                                11: "v_calificacion_jurado_v",
                                12: "v_calificacion_jurado_pdl",
                                13: "v_calificacion_jurado_ci"
                            }
                            campo_firebase = field_mapping[jurado_num]
                            db.collection("Agrupaciones_dia1").document(candidato_seleccionado).update({
                                campo_firebase: total_score
                            })
                        else:
                            campo_firebase = obtener_campo_firebase(jurado_num, datos['categoria'])
                            db.collection("Agrupaciones_dia1").document(candidato_seleccionado).update({
                                campo_firebase: calificaciones[0]
                            })
                        
                        st.success("Calificación enviada correctamente")
                        st.session_state.confirmacion = False
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error al enviar calificación: {e}")
                else:
                    st.session_state.confirmacion = True
                    st.warning("¿Está seguro de enviar esta calificación? Presione nuevamente para confirmar.")

if __name__ == "__main__":
    main()
