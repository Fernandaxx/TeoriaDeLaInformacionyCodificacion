import csv
import numpy as np

from fuente.simbolos import simbolo_a_binario


def calcular_metricas_huffman(
    frecuencias: np.ndarray,
    codigos: dict,
    orden: int,
    longitud_codificada: int
):

    total_simbolos = np.sum(frecuencias)
    probabilidades = frecuencias / total_simbolos

    largo_promedio_bloque = 0.0
    entropia_bloque = 0.0

    for simbolo, p in enumerate(probabilidades):
        if p > 0:
            largo_codigo = len(codigos[simbolo])
            largo_promedio_bloque += p * largo_codigo
            entropia_bloque -= p * np.log2(p)

    longitud_original = int(total_simbolos * orden)
    largo_promedio_bit = largo_promedio_bloque / orden
    entropia_bit = entropia_bloque / orden
    tasa_compresion = longitud_original / longitud_codificada

    return {
        "orden": orden,
        "total_simbolos": int(total_simbolos),
        "longitud_original_bits": longitud_original,
        "longitud_codificada_bits": int(longitud_codificada),
        "largo_promedio_bloque": float(largo_promedio_bloque),
        "largo_promedio_bit": float(largo_promedio_bit),
        "entropia_bloque": float(entropia_bloque),
        "entropia_bit": float(entropia_bit),
        "tasa_compresion": float(tasa_compresion),
    }


def armar_tabla_huffman(frecuencias: np.ndarray, codigos: dict, orden: int):

    total = np.sum(frecuencias)
    filas = []

    for simbolo in range(2 ** orden):
        frecuencia = int(frecuencias[simbolo])
        probabilidad = frecuencia / total if total > 0 else 0.0
        codigo = codigos.get(simbolo, "")

        fila = {
            "simbolo": simbolo,
            "bloque_binario": simbolo_a_binario(simbolo, orden),
            "frecuencia": frecuencia,
            "probabilidad": probabilidad,
            "codigo_huffman": codigo,
            "longitud_codigo": len(codigo),
        }

        filas.append(fila)

    return filas


def guardar_csv(filas: list, ruta_salida: str):
 
    if len(filas) == 0:
        return

    claves = filas[0].keys()

    with open(ruta_salida, "w", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=claves)
        escritor.writeheader()
        escritor.writerows(filas)


def imprimir_tabla_huffman(filas: list):

    print()
    print("Tabla Huffman")
    print("-" * 80)
    print(
        "{:<8} {:<12} {:<12} {:<14} {:<15} {:<10}".format(
            "m",
            "bloque",
            "freq",
            "prob",
            "codigo",
            "largo"
        )
    )
    print("-" * 80)

    for fila in filas:
        print(
            "{:<8} {:<12} {:<12} {:<14.8f} {:<15} {:<10}".format(
                fila["simbolo"],
                fila["bloque_binario"],
                fila["frecuencia"],
                fila["probabilidad"],
                fila["codigo_huffman"],
                fila["longitud_codigo"],
            )
        )