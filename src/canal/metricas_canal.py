import numpy as np


def calcular_metricas(
    U: np.ndarray,
    U_e: np.ndarray,
    filas_aceptadas: np.ndarray
) -> dict:

    U_ref = U[filas_aceptadas]

    total_palabras = U_ref.shape[0]
    k = U.shape[1]

    palabras_descartadas = int(U.shape[0] - total_palabras)

    if total_palabras == 0:
        return {
            "palabras_comparadas": 0,
            "palabras_descartadas": palabras_descartadas,
            "errores_palabra": 0,
            "errores_bit": 0,
            "Pep": np.nan,
            "Peb": np.nan,
            "P_descartadas": 1.0,
            "P_error_no_detectado_sobre_total": 0.0,
        }

    E = (U_e != U_ref)

    errores_palabra = int(np.sum(np.any(E, axis=1)))
    errores_bit = int(np.sum(E))

    Pep = errores_palabra / total_palabras
    Peb = errores_bit / (total_palabras * k)

    return {
        "palabras_comparadas": int(total_palabras),
        "palabras_descartadas": palabras_descartadas,
        "errores_palabra": errores_palabra,
        "errores_bit": errores_bit,
        "Pep": Pep,
        "Peb": Peb,
        "P_descartadas": palabras_descartadas / U.shape[0],
        "P_error_no_detectado_sobre_total": errores_palabra / U.shape[0],
    }