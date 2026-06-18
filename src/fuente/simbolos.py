import numpy as np


def agrupar_bits(bits: np.ndarray, orden: int):
  
    resto = len(bits) % orden

    if resto == 0:
        padding = 0
    else:
        padding = orden - resto

    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

    bloques = bits.reshape(-1, orden)

    return bloques.astype(np.uint8), padding


def bloques_a_decimal(bloques: np.ndarray, orden: int):

    pesos = 2 ** np.arange(orden - 1, -1, -1)
    simbolos = bloques @ pesos

    return simbolos.astype(int)


def simbolos_a_bits(simbolos: np.ndarray, orden: int):
 
    if len(simbolos) == 0:
        return np.array([], dtype=np.uint8)

    desplazamientos = np.arange(orden - 1, -1, -1)
    bits = ((simbolos[:, None] >> desplazamientos) & 1).astype(np.uint8)

    return bits.reshape(-1)


def simbolo_a_binario(simbolo: int, orden: int) -> str:
  
    return format(simbolo, "0{}b".format(orden))