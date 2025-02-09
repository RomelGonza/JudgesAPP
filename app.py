import streamlit as st
from src.auth import login, logout, check_session
from src.firebase_config import init_firebase
from src.utils import (
    obtener_numero_jurado,
    obtener_criterio_calificacion,
    get_max_score,
    obtener_campo_firebase,
    cargar_candidatos,
    actualizar_calificacion,
    verificar_calificacion_existente,
    obtener_subcriterios
)

def main():
    st.set_page_config(
        page_title="Candelaria Luces",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)    


    
    # Autenticación
    if not check_session():
        if not login():
            return

    # Sidebar con botón de logout
    with st.sidebar:
        if st.button("Cerrar Sesión"):
            logout()
            return

    st.title("Candelaria Traje de Luces - Estadio")

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
        format_func=lambda x: dict(candidatos)[x] if x else "Seleccione un conjunto",
        key="selector_conjunto"
    )

    if candidato_seleccionado:
        try:
            # Obtener datos del conjunto
            doc = db.collection("luces_day_one").document(candidato_seleccionado).get()
            datos = doc.to_dict()
    
            # Verificar si ya existe calificación
            calificacion_existe = verificar_calificacion_existente(db, candidato_seleccionado, jurado_num, datos['categoria'])
    
            # Mostrar datos del conjunto
            st.write("### Calificación")
            st.write(f"Conjunto N°{datos['numero']}: {datos['nombre_del_conjunto']}")
            st.write(f"Categoría: {datos['categoria']}")

            if calificacion_existe:
                st.warning("⚠️ Ya has calificado a este conjunto. No se permite modificar la calificación.")
                # Mostrar la calificación existente
                campo = obtener_campo_firebase(jurado_num, datos['categoria'])
                st.info(f"Calificación enviada: {datos[campo]}")
            else:
                # Input de calificación
                if jurado_num in [10, 11, 12, 13]:
                    calificaciones = []
                    criterios = obtener_subcriterios(jurado_num)
                    for criterio in criterios:
                        # Usar None como valor por defecto
                        cal = st.number_input(
                            f"Calificación - {criterio}",
                            min_value=0.0,
                            max_value=10.0,
                            step=0.5,
                            value=None,  # Valor inicial None
                            placeholder="Ingrese calificación",
                            key=f"cal_{criterio}"
                        )
                        # Solo agregar la calificación si se ha ingresado un valor
                        if cal is not None:
                            calificaciones.append(cal)
                else:
                    max_valor = get_max_score(criterio, datos['categoria'])
                    # Usar None como valor por defecto
                    calificacion = st.number_input(
                        f"Calificación - {criterio}",
                        min_value=0.0,
                        max_value=float(max_valor),
                        step=0.5,
                        value=None,  # Valor inicial None
                        placeholder="Ingrese calificación",
                        key=f"cal_single"
                    )
                    calificaciones = [calificacion] if calificacion is not None else []
    
                # Estilo para el botón verde
                st.markdown("""
                    <style>
                        div.stButton > button {
                            background-color: #28a745;
                            color: white !important;
                            border: none;
                            padding: 0.5rem 1rem;
                            font-size: 1rem;
                            font-weight: 600;
                        }
                        div.stButton > button:hover {
                            background-color: #218838;
                            color: white !important;
                            border: none;
                        }
                        div.stButton > button:active, 
                        div.stButton > button:focus,
                        div.stButton > button:focus:not(:active) {
                            background-color: #1e7e34;
                            color: white !important;
                            border: none;
                            box-shadow: none;
                        }
                        div.stButton > button:visited {
                            color: white !important;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                # El botón siempre está presente
                if st.button("Enviar Calificación"):
                    # Validación al momento de enviar
                    if len(calificaciones) == 0:
                        st.error("Por favor, ingrese una calificación antes de enviar.")
                        return
                        
                    if st.session_state.get('confirmacion', False):
                        try:
                            # Verificar que todas las calificaciones estén ingresadas
                            if jurado_num in [10, 11, 12, 13] and len(calificaciones) != len(criterios):
                                st.error("Por favor, ingrese todas las calificaciones antes de enviar.")
                                st.session_state.confirmacion = False
                                return
                            
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
