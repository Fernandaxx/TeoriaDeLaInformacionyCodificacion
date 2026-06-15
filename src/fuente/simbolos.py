import numpy as np


def agrupar_bits(bits: np.ndarray, orden: int):
    """
    Agrupa bits en bloques de longitud 'orden'.

    Ejemplo orden 2:
        0 1 1 0 -> 01, 10

    Si la cantidad de bits no es múltiplo del orden, agrega ceros al final.
    """
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
    """
    Convierte cada bloque binario a decimal.

    Orden 2:
        00 -> 0
        01 -> 1
        10 -> 2
        11 -> 3

    Orden 3:
        000 -> 0
        ...
        111 -> 7

    En C haríamos un for acumulando potencias de 2.
    En NumPy usamos producto matricial vectorizado.
    """
    pesos = 2 ** np.arange(orden - 1, -1, -1)
    simbolos = bloques @ pesos

    return simbolos.astype(int)


def simbolos_a_bits(simbolos: np.ndarray, orden: int):
    """
    Convierte símbolos decimales nuevamente a bits.
    Se usará después para reconstruir la imagen en el opcional 2.
    """
    if len(simbolos) == 0:
        return np.array([], dtype=np.uint8)

    desplazamientos = np.arange(orden - 1, -1, -1)
    bits = ((simbolos[:, None] >> desplazamientos) & 1).astype(np.uint8)

    return bits.reshape(-1)


def simbolo_a_binario(simbolo: int, orden: int) -> str:
    """
    Devuelve la representación binaria de un símbolo.
    """
    return format(simbolo, "0{}b".format(orden))