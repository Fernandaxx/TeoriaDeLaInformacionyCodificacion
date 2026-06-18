import os
import csv
import numpy as np

from canal.config_canal import K, N, A, NUM_PALABRAS, SEED, EBN0_DB_VECTOR
from canal.matrices import (
    generar_matriz_generadora,
    generar_matriz_verificadora_de_paridad,
    verificar_ortogonalidad,
    calcular_dmin,
    ganancia_asintotica_corrector_db,
)
from canal.simulador_canal import simular_curva
from canal.graficos_canal import graficar_resultados_canal

from fuente.simulador_fuente import ejecutar_huffman_ordenes_2_y_3
from fuente.opcional2 import ejecutar_opcional_2_ordenes_2_y_3


def guardar_csv(resultados: list, ruta_salida: str):

    if len(resultados) == 0:
        return

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    claves = resultados[0].keys()

    with open(ruta_salida, "w", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=claves)
        escritor.writeheader()
        escritor.writerows(resultados)


def ejecutar_parte_canal():
    """
    Ejecuta la simulación completa de codificación de canal:
        - matrices G y H
        - distancia mínima
        - capacidad correctora y detectora
        - curvas en modo corrector
        - curvas en modo detector
    """

    print()
    print("=" * 100)
    print("PARTE 1 - CODIFICACIÓN DE CANAL")
    print("=" * 100)

    G = generar_matriz_generadora(K, N)
    H = generar_matriz_verificadora_de_paridad(G)

    GHt = verificar_ortogonalidad(G, H)

    d_min = calcular_dmin(G)
    
    tc = (d_min - 1) // 2
    td = d_min - 1

    ganancia_db = ganancia_asintotica_corrector_db(K, N, tc)

    print()
    print("Matriz generadora G:")
    print(G)

    print()
    print("Matriz de control de paridad H:")
    print(H)

    print()
    print("Verificación G @ H.T mod 2:")
    print(GHt)

    print()
    print("Parámetros del código")
    print("-" * 50)
    print("Código: ({},{})".format(N, K))
    print("d_min = {}".format(d_min))
    print("Corrige hasta t = {} error/es por palabra".format(tc))
    print("Detecta hasta {} error/es por palabra".format(td))
    print("Ganancia asintótica aproximada = {:.4f} dB".format(ganancia_db))

    resultados_corrector = simular_curva(
        EbfN0_db_vector=EBN0_DB_VECTOR,
        num_palabras=NUM_PALABRAS,
        k=K,
        n=N,
        A=A,
        modo="corrector",
    )

    guardar_csv(
        resultados_corrector,
        "src/resultados/tablas/canal_corrector.csv"
    )

    graficar_resultados_canal(
        resultados=resultados_corrector,
        k=K,
        n=N,
        d_min=d_min,
        modo="corrector",
        ruta_salida="src/resultados/figuras/canal_corrector.png",
        G=G,
    )

    resultados_detector = simular_curva(
        EbfN0_db_vector=EBN0_DB_VECTOR,
        num_palabras=NUM_PALABRAS,
        k=K,
        n=N,
        A=A,
        modo="detector",
    )

    guardar_csv(
        resultados_detector,
        "src/resultados/tablas/canal_detector.csv"
    )

    graficar_resultados_canal(
        resultados=resultados_detector,
        k=K,
        n=N,
        d_min=d_min,
        modo="detector",
        ruta_salida="src/resultados/figuras/canal_detector.png",
        G=G,
    )

    return {
        "G": G,
        "H": H,
        "d_min": d_min,
        "tc": tc,
        "td": td,
        "ganancia_db": ganancia_db,
        "resultados_corrector": resultados_corrector,
        "resultados_detector": resultados_detector,
    }


def ejecutar_parte_fuente():
    """
    Ejecuta la codificación de fuente con Huffman:
        - orden 2
        - orden 3
        - tablas de probabilidades
        - códigos Huffman
        - largo promedio
        - tasa de compresión
    """

    print()
    print("=" * 100)
    print("PARTE 2 - CODIFICACIÓN DE FUENTE HUFFMAN")
    print("=" * 100)

    ruta_imagen = "src/fuente/logo FI.tif"

    resultados_huffman = ejecutar_huffman_ordenes_2_y_3(
        ruta_imagen=ruta_imagen,
        carpeta_tablas="src/resultados/tablas"
    )

    return resultados_huffman


def main():
    np.random.seed(SEED)

    os.makedirs("src/resultados/figuras", exist_ok=True)
    os.makedirs("src/resultados/tablas", exist_ok=True)
    os.makedirs("src/resultados/imagenes", exist_ok=True)

    ejecutar_parte_canal()
    ejecutar_parte_fuente()

    ejecutar_opcional_2_ordenes_2_y_3(
    ruta_imagen="src/fuente/logo FI.tif",
    ebn0_db=10.0
)

    print()
    print("=" * 100)
    print("EJECUCIÓN FINALIZADA")
    print("=" * 100)

    print()
    print("Archivos generados:")
    print("- src/resultados/tablas/canal_corrector.csv")
    print("- src/resultados/tablas/canal_detector.csv")
    print("- src/resultados/tablas/huffman_orden2.csv")
    print("- src/resultados/tablas/huffman_orden3.csv")
    print("- src/resultados/tablas/resumen_huffman.csv")
    print("- src/resultados/figuras/canal_corrector.png")
    print("- src/resultados/figuras/canal_detector.png")


if __name__ == "__main__":
    main()