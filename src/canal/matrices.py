import numpy as np


def generar_matriz_generadora(k: int = 10, n: int = 14) -> np.ndarray:
    """
    Genera la matriz generadora sistemática G = [I_k | P].
    Código de bloque lineal (14,10).
    """
    if k != 10 or n != 14:
        raise ValueError("Esta matriz está definida para el código (14,10).")

    I_k = np.eye(k, dtype=np.uint8)

    P = np.array([
        [0, 0, 1, 1],
        [0, 1, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 0, 0],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ], dtype=np.uint8)

    G = np.concatenate((I_k, P), axis=1)
    return G.astype(np.uint8)


def generar_matriz_verificadora_de_paridad(G: np.ndarray) -> np.ndarray:
    """
    Si G = [I_k | P], entonces H = [P.T | I_(n-k)].
    """
    k, n = G.shape

    P = G[:, k:]
    I_paridad = np.eye(n - k, dtype=np.uint8)

    H = np.concatenate((P.T, I_paridad), axis=1)
    return H.astype(np.uint8)


def verificar_ortogonalidad(G: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Verifica que G H.T = 0 mod 2.
    """
    return (G @ H.T) % 2


def calcular_dmin(G: np.ndarray) -> int:
    """
    Calcula la distancia mínima generando todas las palabras no nulas.

    Para k = 10 hay 2^10 - 1 = 1023 combinaciones, así que este for es aceptable.
    """
    k, _ = G.shape
    d_min = None

    for i in range(1, 2 ** k):
        u = np.array(list(np.binary_repr(i, width=k)), dtype=np.uint8)
        v = (u @ G) % 2
        peso = int(np.sum(v))

        if d_min is None or peso < d_min:
            d_min = peso

    return int(d_min)

#revisar 
def ganancia_asintotica_corrector_db(k: int, n: int, t: int) -> float:
    """
    Ganancia de codificación asintótica aproximada para decodificación dura.

    gamma = R * (t + 1)
    Gc[dB] = 10 log10(gamma)
    """
    R = k / n
    gamma = R * (t + 1)
    return 10 * np.log10(gamma)