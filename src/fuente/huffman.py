import heapq
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(order=True)
class NodoHuffman:
    frecuencia: int
    orden_heap: int = field(compare=True)
    simbolo: Optional[int] = field(default=None, compare=False)
    izquierda: Optional["NodoHuffman"] = field(default=None, compare=False)
    derecha: Optional["NodoHuffman"] = field(default=None, compare=False)


def calcular_frecuencias(simbolos: np.ndarray, orden: int):
    """
    Cuenta la frecuencia absoluta de cada símbolo posible.

    Para orden 2 hay 2^2 = 4 símbolos.
    Para orden 3 hay 2^3 = 8 símbolos.
    """
    cantidad_simbolos_posibles = 2 ** orden

    frecuencias = np.bincount(
        simbolos,
        minlength=cantidad_simbolos_posibles
    )

    return frecuencias.astype(int)


def calcular_probabilidades(frecuencias: np.ndarray):
    """
    Calcula frecuencia relativa de cada símbolo.
    """
    total = np.sum(frecuencias)

    if total == 0:
        raise ValueError("No hay símbolos para calcular probabilidades.")

    return frecuencias / total


def construir_arbol_huffman(frecuencias: np.ndarray):
    """
    Construye el árbol de Huffman usando una cola de prioridad.

    heapq siempre extrae el nodo de menor frecuencia.
    """
    heap = []
    contador = 0

    for simbolo, frecuencia in enumerate(frecuencias):
        if frecuencia > 0:
            nodo = NodoHuffman(
                frecuencia=int(frecuencia),
                orden_heap=contador,
                simbolo=simbolo
            )
            heapq.heappush(heap, nodo)
            contador += 1

    if len(heap) == 0:
        raise ValueError("No hay símbolos para codificar.")

    if len(heap) == 1:
        return heap[0]

    while len(heap) > 1:
        nodo_izq = heapq.heappop(heap)
        nodo_der = heapq.heappop(heap)

        nodo_padre = NodoHuffman(
            frecuencia=nodo_izq.frecuencia + nodo_der.frecuencia,
            orden_heap=contador,
            simbolo=None,
            izquierda=nodo_izq,
            derecha=nodo_der
        )

        contador += 1
        heapq.heappush(heap, nodo_padre)

    return heap[0]


def generar_codigos_huffman(nodo: NodoHuffman, prefijo: str = ""):
    """
    Recorre el árbol y arma el diccionario:

        símbolo decimal -> código Huffman
    """
    if nodo.simbolo is not None:
        if prefijo == "":
            prefijo = "0"
        return {nodo.simbolo: prefijo}

    codigos = {}

    codigos.update(
        generar_codigos_huffman(nodo.izquierda, prefijo + "0")
    )

    codigos.update(
        generar_codigos_huffman(nodo.derecha, prefijo + "1")
    )

    return codigos


def codificar_huffman(simbolos: np.ndarray, codigos: dict):
    """
    Codifica la secuencia de símbolos usando el diccionario Huffman.

    Devuelve un vector de bits 0/1.
    """
    cadena = "".join(codigos[int(s)] for s in simbolos)

    bits_codificados = np.fromiter(
        (int(bit) for bit in cadena),
        dtype=np.uint8
    )

    return bits_codificados


def preparar_decodificador_huffman(codigos: dict):
    """
    Invierte el diccionario:

        código Huffman -> símbolo
    """
    decodificador = {}

    for simbolo, codigo in codigos.items():
        decodificador[codigo] = simbolo

    return decodificador


def decodificar_huffman(bits_codificados: np.ndarray, codigos: dict):
    """
    Decodifica una secuencia de bits Huffman.

    Se usa más adelante para el opcional 2.
    """
    decodificador = preparar_decodificador_huffman(codigos)

    buffer = ""
    simbolos_decodificados = []

    for bit in bits_codificados:
        buffer += str(int(bit))

        if buffer in decodificador:
            simbolos_decodificados.append(decodificador[buffer])
            buffer = ""

    return np.array(simbolos_decodificados, dtype=int), buffer