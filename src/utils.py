def obtener_numero_jurado(email):
    """Obtiene el número de jurado según el email"""
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
    """Obtiene el criterio de calificación según el número de jurado"""
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

def cargar_candidatos(db):
    """
    Carga la lista de candidatos desde Firebase incluyendo el número del conjunto
    """
    try:
        candidatos = []
        docs = db.collection("luces_day_one").stream()
        
        for doc in docs:
            datos = doc.to_dict()
            numero = datos.get('numero', 'S/N')  # Obtiene el número del conjunto
            nombre = datos.get('nombre_del_conjunto', 'Sin nombre')
            # Guarda una tupla con (id, nombre_con_numero)
            candidatos.append((doc.id, f"N°{numero} - {nombre}"))
            
        # Ordenar por número de conjunto
        candidatos.sort(key=lambda x: int(x[1].split('°')[1].split(' -')[0]))
        return candidatos
    except Exception as e:
        st.error(f"Error al cargar candidatos: {e}")
        return []

def get_max_score(criterio, categoria):
    """
    Obtiene el puntaje máximo según el criterio y la categoría
    """
    puntajes_maximos = {
        "PRESENTACION Y VESTIMENTA": {
            "CARNAVALEZCAS LIGERAS": 20,
            "SIKURIS DE UN SOLO BOMBO": 20,
            "SIKURIS VARIOS BOMBOS": 20,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 20,
            "default": 20
        },
        "MUSICA": {
            "CARNAVALEZCAS LIGERAS": 30,
            "SIKURIS DE UN SOLO BOMBO": 30,
            "SIKURIS VARIOS BOMBOS": 30,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 30,
            "default": 30
        },
        "COREOGRAFIA": {
            "CARNAVALEZCAS LIGERAS": 20,
            "SIKURIS DE UN SOLO BOMBO": 20,
            "SIKURIS VARIOS BOMBOS": 20,
            "AYARACHIS, ISLA SIKURIS Y KANTU": 20,
            "default": 20
        },
        "MUSICA(danzarines y musicos)": {
            "default": 10
        },
        "VESTIMENTA(danzarines y musicos)": {
            "default": 10
        },
        "RECORRIDO(desplazamiento)": {
            "default": 7
        },
        "Brigada Ecologica": {
            "default": 3
        }
    }
    
    # Obtener los puntajes para el criterio específico
    criterio_puntajes = puntajes_maximos.get(criterio, {"default": 30})
    
    # Obtener el puntaje máximo para la categoría específica o usar el valor por defecto
    return criterio_puntajes.get(categoria, criterio_puntajes["default"])

def obtener_campo_firebase(jurado_num, categoria):
    """
    Obtiene el nombre del campo en Firebase según el número de jurado y la categoría.
    Para los jurados 1-9, el número se incluye en el nombre del campo.
    Para los jurados 10-13, el nombre del campo es fijo.
    """
    # Mapeo de rangos de jurados a sus sufijos de campo
    campos_por_jurado = {
        (1, 2, 3): "e_calificacion_jurado{}_pv",  # Presentación y Vestimenta
        (4, 5, 6): "e_calificacion_jurado{}_m",   # Música
        (7, 8, 9): "e_calificacion_jurado{}_c",   # Coreografía
        (10,): "v_calificacion_jurado_mc",      # Música (danzarines y músicos)
        (11,): "v_calificacion_jurado_v",       # Vestimenta
        (12,): "v_calificacion_jurado_pdl",     # Recorrido
        (13,): "v_calificacion_jurado_ci"       # Brigada Ecológica
    }
    
    # Encontrar el campo correspondiente al número de jurado
    for jurados, campo_template in campos_por_jurado.items():
        if jurado_num in jurados:
            # Si es uno de los primeros 9 jurados, incluir el número en el nombre del campo
            if jurado_num <= 9:
                return campo_template.format(jurado_num)
            # Para los jurados 10-13, usar el nombre fijo
            return campo_template
            
    raise ValueError(f"No se encontró campo para el jurado {jurado_num}")

def actualizar_calificacion(db, candidato_id, jurado_num, calificaciones, categoria):
    """Actualiza la calificación en Firebase"""
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
        else:
            campo_firebase = obtener_campo_firebase(jurado_num, categoria)
            total_score = calificaciones[0]

        db.collection("luces_day_one").document(candidato_id).update({
            campo_firebase: total_score
        })
        return True
    except Exception as e:
        st.error(f"Error al actualizar calificación: {e}")
        return False


def verificar_calificacion_existente(db, candidato_id, jurado_num, categoria):
    """
    Verifica si ya existe una calificación diferente de 0 para este jurado y candidato.
    """
    try:
        # Obtener el documento del candidato
        doc = db.collection("luces_day_one").document(candidato_id).get()
        if not doc.exists:
            return False

        # Obtener el campo correspondiente
        campo = obtener_campo_firebase(jurado_num, categoria)
        datos = doc.to_dict()
        
        # Si el campo no existe, retornar False
        if campo not in datos:
            return False
            
        calificacion = datos[campo]
        
        # Si la calificación es None o 0, retornar False
        if calificacion is None or calificacion == 0:
            return False
            
        # Convertir a float si es string
        if isinstance(calificacion, str):
            try:
                calificacion = float(calificacion)
                return calificacion > 0
            except ValueError:
                return False
                
        # Si la calificación es numérica, verificar si es mayor que 0
        return float(calificacion) > 0
        
    except Exception as e:
        st.error(f"Error al verificar calificación existente: {e}")
        return False
