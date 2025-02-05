import streamlit as st
from src.auth import login, logout, check_session
from src.firebase_config import init_firebase
from src.utils import (
    obtener_numero_jurado,
    obtener_criterio_calificacion,
    get_max_score,
    obtener_campo_firebase,
    cargar_candidatos,
    actualizar_calificacion
)

def main():
    st.set_page_config(
        page_title="Candelaria Originarios",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Autenticación
    if not check_session():
        if not login():
            return

    # Sidebar con botón de logout
    with st.sidebar:
        if st.button("Cerrar Sesión"):
            logout()
            return

    st.title("Candelaria Originarios")

    # Inicializar Firebase
    db = init_firebase()
    if not db:
        st.error("Error al conectar con la base de datos")
        return

    # Obtener información del jurado
    email = st.session_state.user_email
    jurado_num = obtener_numero_jurado(email)
    criterio = obtener_criterio_calificacion(jurado_num)

    st.sidebar.write(f"Criterio de calificación: {criterio}")

    # Cargar y mostrar candidatos
    candidatos = cargar_candidatos(db)
    candidato_seleccionado = st.selectbox(
        "Seleccione un conjunto",
        options=[c[0] for c in candidatos],
        format_func=lambda x: dict(candidatos)[x] if x else "Seleccione un conjunto"
    )

# ... resto del código ...

    if candidato_seleccionado:
        try:
            # Obtener datos del conjunto
            doc = db.collection("Agrupaciones_dia1").document(candidato_seleccionado).get()
            datos = doc.to_dict()
    
            # Verificar si ya existe calificación
            if verificar_calificacion_existente(db, candidato_seleccionado, jurado_num, datos['categoria']):
                st.warning("⚠️ Ya has calificado a este conjunto. No se permite modificar la calificación.")
                # Mostrar la calificación existente
                campo = obtener_campo_firebase(jurado_num, datos['categoria'])
                st.info(f"Calificación enviada: {datos[campo]}")
            else:
                st.write("### Calificación")
                st.write(f"Conjunto: {datos['nombre_del_conjunto']}")
                st.write(f"Categoría: {datos['categoria']}")
    
                # Input de calificación
                if jurado_num in [10, 11, 12, 13]:
                    calificaciones = []
                    criterios = obtener_subcriterios(jurado_num)
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
                            exito = actualizar_calificacion(
                                db,
                                candidato_seleccionado,
                                jurado_num,
                                calificaciones,
                                datos['categoria']
                            )
                            if exito:
                                st.success("✅ Calificación enviada correctamente")
                                st.session_state.confirmacion = False
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error al enviar calificación: {e}")
                    else:
                        st.session_state.confirmacion = True
                        st.warning("⚠️ ¿Está seguro de enviar esta calificación? Presione nuevamente para confirmar.")
                        st.info("⚠️ Recuerde que una vez enviada la calificación, no podrá modificarla.")
    
        except Exception as e:
            st.error(f"Error al cargar datos del conjunto: {e}")

if __name__ == "__main__":
    main()
