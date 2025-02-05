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

def obtener_campo_firebase(jurado_num, categoria):
    """Obtiene el campo de Firebase según el número de jurado"""
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
