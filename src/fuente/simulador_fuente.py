import os

from fuente.imagen import cargar_imagen_binaria
from fuente.simbolos import agrupar_bits, bloques_a_decimal
from fuente.huffman import (
    calcular_frecuencias,
    construir_arbol_huffman,
    generar_codigos_huffman,
    codificar_huffman,
)
from fuente.metricas_fuente import (
    calcular_metricas_huffman,
    armar_tabla_huffman,
    guardar_csv,
    imprimir_tabla_huffman,
)


def ejecutar_huffman_para_orden(
    ruta_imagen: str,
    orden: int,
    carpeta_tablas: str = "src/resultados/tablas"
):
   
    os.makedirs(carpeta_tablas, exist_ok=True)

    imagen_binaria, bits_imagen = cargar_imagen_binaria(ruta_imagen)

    bloques, padding = agrupar_bits(bits_imagen, orden)
    simbolos = bloques_a_decimal(bloques, orden)

    frecuencias = calcular_frecuencias(simbolos, orden)

    arbol = construir_arbol_huffman(frecuencias)
    codigos = generar_codigos_huffman(arbol)

    bits_codificados = codificar_huffman(simbolos, codigos)

    metricas = calcular_metricas_huffman(
        frecuencias=frecuencias,
        codigos=codigos,
        orden=orden,
        longitud_codificada=len(bits_codificados)
    )

    tabla = armar_tabla_huffman(
        frecuencias=frecuencias,
        codigos=codigos,
        orden=orden
    )

    ruta_tabla = os.path.join(
        carpeta_tablas,
        "huffman_orden{}.csv".format(orden)
    )

    guardar_csv(tabla, ruta_tabla)

    print()
    print("=" * 100)
    print("HUFFMAN - FUENTE EXTENDIDA DE ORDEN {}".format(orden))
    print("=" * 100)

    print("Imagen binaria shape:              {}".format(imagen_binaria.shape))
    print("Cantidad de bits originales:       {}".format(len(bits_imagen)))
    print("Padding agregado a fuente:         {}".format(padding))
    print("Cantidad de símbolos extendidos:   {}".format(len(simbolos)))
    print("Longitud codificada [bits]:        {}".format(len(bits_codificados)))
    print("Largo promedio por bloque:         {:.6f}".format(metricas["largo_promedio_bloque"]))
    print("Largo promedio por bit de fuente:  {:.6f}".format(metricas["largo_promedio_bit"]))
    print("Entropía por bloque:               {:.6f}".format(metricas["entropia_bloque"]))
    print("Entropía por bit:                  {:.6f}".format(metricas["entropia_bit"]))
    print("Tasa de compresión:                {:.6f}".format(metricas["tasa_compresion"]))
    print("Tabla guardada en:                 {}".format(ruta_tabla))

    imprimir_tabla_huffman(tabla)

    return {
        "orden": orden,
        "imagen_binaria": imagen_binaria,
        "bits_imagen": bits_imagen,
        "bloques": bloques,
        "padding": padding,
        "simbolos": simbolos,
        "frecuencias": frecuencias,
        "codigos": codigos,
        "bits_codificados": bits_codificados,
        "metricas": metricas,
        "tabla": tabla,
        "ruta_tabla": ruta_tabla,
    }


def ejecutar_huffman_ordenes_2_y_3(
    ruta_imagen: str,
    carpeta_tablas: str = "src/resultados/tablas"
):
   
    resultado_orden2 = ejecutar_huffman_para_orden(
        ruta_imagen=ruta_imagen,
        orden=2,
        carpeta_tablas=carpeta_tablas
    )

    resultado_orden3 = ejecutar_huffman_para_orden(
        ruta_imagen=ruta_imagen,
        orden=3,
        carpeta_tablas=carpeta_tablas
    )

    resumen = [
        resultado_orden2["metricas"],
        resultado_orden3["metricas"],
    ]

    ruta_resumen = os.path.join(carpeta_tablas, "resumen_huffman.csv")
    guardar_csv(resumen, ruta_resumen)

    print()
    print("=" * 100)
    print("RESUMEN HUFFMAN")
    print("=" * 100)

    print(
        "{:<10} {:<20} {:<20} {:<20}".format(
            "Orden",
            "Lprom/bloque",
            "Lprom/bit",
            "Tasa compresión"
        )
    )

    for r in resumen:
        print(
            "{:<10} {:<20.6f} {:<20.6f} {:<20.6f}".format(
                r["orden"],
                r["largo_promedio_bloque"],
                r["largo_promedio_bit"],
                r["tasa_compresion"],
            )
        )

    print()
    print("Resumen guardado en: {}".format(ruta_resumen))

    return {
        "orden2": resultado_orden2,
        "orden3": resultado_orden3,
        "ruta_resumen": ruta_resumen,
    }