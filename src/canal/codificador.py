import numpy as np


def generar_fuente(num_palabras: int, k: int) -> np.ndarray:

    return np.random.randint(0, 2, size=(num_palabras, k), dtype=np.uint8)


def codificar(U: np.ndarray, G: np.ndarray) -> np.ndarray:

    V = (U @ G) % 2
    return V.astype(np.uint8)


def decodificar_sistematico(V_e: np.ndarray, k: int) -> np.ndarray:

    return V_e[:, :k].astype(np.uint8)


def completar_multiplo(bits: np.ndarray, multiplo: int):
    
    resto = len(bits) % multiplo

    if resto == 0:
        padding = 0
    else:
        padding = multiplo - resto

    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

    return bits.astype(np.uint8), padding