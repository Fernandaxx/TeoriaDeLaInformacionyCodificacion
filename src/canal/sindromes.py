import numpy as np
from itertools import combinations


def calcular_sindromes(R: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Calcula:
        S = R H.T mod 2
    """
    S = (R @ H.T) % 2
    return S.astype(np.uint8)


def generar_tabla_sindromes(H: np.ndarray, t: int) -> dict:
    """
    Genera una tabla:
        síndrome -> patrón de error

    Para d_min = 3, t = 1.
    Entonces corrige errores de un solo bit.
    """
    n = H.shape[1]
    tabla = {}

    for peso in range(1, t + 1):
        for indices in combinations(range(n), peso):
            e = np.zeros(n, dtype=np.uint8)
            e[list(indices)] = 1

            sindrome = (e @ H.T) % 2
            tabla[tuple(sindrome)] = e

    return tabla


def corregir_por_sindrome(R: np.ndarray, H: np.ndarray, d_min: int):
    """
    Modo corrector:
    si el síndrome coincide con un patrón corregible, se corrige la palabra.
    """
    S = calcular_sindromes(R, H)

    t = (d_min - 1) // 2
    tabla = generar_tabla_sindromes(H, t)

    V_e = R.copy()

    cantidad_sindromes_no_nulos = int(np.sum(~np.all(S == 0, axis=1)))
    cantidad_corregidas = 0

    for sindrome, error_estimado in tabla.items():
        mascara = np.all(S == np.array(sindrome, dtype=np.uint8), axis=1)

        if np.any(mascara):
            V_e[mascara] = (V_e[mascara] + error_estimado) % 2
            cantidad_corregidas += int(np.sum(mascara))

    filas_aceptadas = np.ones(R.shape[0], dtype=bool)

    estadisticas = {
        "sindromes_no_nulos": cantidad_sindromes_no_nulos,
        "palabras_corregidas": cantidad_corregidas,
        "palabras_descartadas": 0,
    }

    return V_e.astype(np.uint8), S, filas_aceptadas, estadisticas


def detectar_por_sindrome(R: np.ndarray, H: np.ndarray):
    """
    Modo detector:
    las palabras con síndrome no nulo se descartan.
    """
    S = calcular_sindromes(R, H)

    sindrome_cero = np.all(S == 0, axis=1)

    filas_aceptadas = sindrome_cero
    V_e = R[filas_aceptadas].copy()

    palabras_descartadas = int(R.shape[0] - V_e.shape[0])

    estadisticas = {
        "sindromes_no_nulos": palabras_descartadas,
        "palabras_corregidas": 0,
        "palabras_descartadas": palabras_descartadas,
    }

    return V_e.astype(np.uint8), S, filas_aceptadas, estadisticas


def detector_corrector(R: np.ndarray, H: np.ndarray, d_min: int, modo: str):
    if modo == "corrector":
        return corregir_por_sindrome(R, H, d_min)

    if modo == "detector":
        return detectar_por_sindrome(R, H)

    raise ValueError("modo debe ser 'corrector' o 'detector'.")