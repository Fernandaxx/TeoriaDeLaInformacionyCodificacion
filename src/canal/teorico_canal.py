import numpy as np
from scipy.special import erfc
from math import comb


def Q(x):
    """
    Función Q usando erfc.
    """
    return 0.5 * erfc(x / np.sqrt(2))


def peb_teorica_sin_codigo(EbfN0_db):
    """
    BER teórica de BPSK sin codificación.
    """
    EbfN0 = 10 ** (EbfN0_db / 10)
    return Q(np.sqrt(2 * EbfN0))


def p_error_canal_codificado(EbfN0_db, k: int, n: int):
    """
    Probabilidad de error en el canal para el sistema codificado.

    El eje es Ebf/N0, energía por bit de fuente.
    Como se transmite redundancia:
        R = k/n
        Ebc/N0 = R * Ebf/N0
    """
    R = k / n
    EbfN0 = 10 ** (EbfN0_db / 10)

    return Q(np.sqrt(2 * R * EbfN0))


def pep_teorica_corrector(EbfN0_db, n: int, k: int, t: int):
    """
    Probabilidad teórica aproximada de error de palabra para corrector.

    Falla si aparecen t+1 o más errores en una palabra de largo n.
    """
    p = p_error_canal_codificado(EbfN0_db, k, n)

    Pep = 0.0
    for i in range(t + 1, n + 1):
        Pep += comb(n, i) * (p ** i) * ((1 - p) ** (n - i))

    return Pep


def enumerar_pesos_codigo(G):
    """
    Enumera los pesos de todas las palabras de código.
    Sirve para estimar probabilidad de error no detectado en modo detector.
    """
    k, n = G.shape

    pesos = np.zeros(n + 1, dtype=int)

    for i in range(2 ** k):
        u = np.array(list(np.binary_repr(i, width=k)), dtype=np.uint8)
        v = (u @ G) % 2
        w = int(np.sum(v))
        pesos[w] += 1

    return pesos


def prob_detector_teorica(EbfN0_db, G, k: int, n: int):
    """
    Probabilidades teóricas para modo detector.

    P_error_no_detectado:
        probabilidad de que el patrón de error sea una palabra de código no nula.

    P_descartadas:
        probabilidad de que el síndrome sea no nulo.
    """
    p = p_error_canal_codificado(EbfN0_db, k, n)

    pesos = enumerar_pesos_codigo(G)

    p_sindrome_cero = 0.0
    p_error_no_detectado = 0.0

    for w, cantidad in enumerate(pesos):
        termino = cantidad * (p ** w) * ((1 - p) ** (n - w))
        p_sindrome_cero += termino

        if w > 0:
            p_error_no_detectado += termino

    p_descartadas = 1 - p_sindrome_cero

    return {
        "P_descartadas_teo": p_descartadas,
        "P_error_no_detectado_teo": p_error_no_detectado,
    }