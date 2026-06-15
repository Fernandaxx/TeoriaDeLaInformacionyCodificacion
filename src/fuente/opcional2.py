import os
import numpy as np

from fuente.simulador_fuente import ejecutar_huffman_para_orden
from fuente.huffman import preparar_decodificador_huffman
from fuente.simbolos import simbolos_a_bits
from fuente.imagen import guardar_imagen_binaria, guardar_comparacion_imagenes

from canal.config_canal import K, N, A
from canal.matrices import (
    generar_matriz_generadora,
    generar_matriz_verificadora_de_paridad,
    calcular_dmin,
)
from canal.codificador import codificar, decodificar_sistematico, completar_multiplo
from canal.bpsk_awgn import canal_awgn_bpsk
from canal.sindromes import corregir_por_sindrome


def preparar_prefijos(codigos: dict):
    """
    Arma el conjunto de prefijos válidos del código Huffman.
    Sirve para detectar cuándo un error de canal rompe la sincronización.
    """
    prefijos = set()

    for codigo in codigos.values():
        for i in range(1, len(codigo)):
            prefijos.add(codigo[:i])

    return prefijos


def decodificar_huffman_con_limite(
    bits_codificados: np.ndarray,
    codigos: dict,
    cantidad_simbolos_esperada: int
):
    """
    Decodifica Huffman, pero se detiene cuando recupera la cantidad esperada
    de símbolos.

    Si queda algún error de canal, Huffman puede desincronizarse porque es
    un código de longitud variable. Por eso registramos errores de prefijo.
    """
    decodificador = preparar_decodificador_huffman(codigos)
    prefijos = preparar_prefijos(codigos)

    buffer = ""
    simbolos_decodificados = []
    errores_prefijo = 0

    for bit in bits_codificados:
        buffer += str(int(bit))

        if buffer in decodificador:
            simbolos_decodificados.append(decodificador[buffer])
            buffer = ""

            if len(simbolos_decodificados) == cantidad_simbolos_esperada:
                break

        elif buffer not in prefijos:
            errores_prefijo += 1
            buffer = ""

    return np.array(simbolos_decodificados, dtype=int), errores_prefijo, buffer


def transmitir_bits_por_canal(bits_tx: np.ndarray, ebn0_db: float):
    """
    Transmite una secuencia de bits usando el código de canal (14,10).

    Flujo:
        bits_tx -> bloques de K -> codificación canal -> AWGN/BPSK
        -> corrección por síndrome -> bits_rx
    """
    G = generar_matriz_generadora(K, N)
    H = generar_matriz_verificadora_de_paridad(G)
    d_min = calcular_dmin(G)

    bits_tx_rellenados, padding_canal = completar_multiplo(bits_tx, K)

    U = bits_tx_rellenados.reshape(-1, K)

    V = codificar(U, G)

    R_bits, _, _ = canal_awgn_bpsk(
        V=V,
        A=A,
        n=N,
        k=K,
        EbfN0_db=ebn0_db
    )

    V_corr, _, _, estadisticas = corregir_por_sindrome(
        R=R_bits,
        H=H,
        d_min=d_min
    )

    U_estimada = decodificar_sistematico(V_corr, K)

    bits_rx = U_estimada.reshape(-1)

    if padding_canal > 0:
        bits_rx = bits_rx[:-padding_canal]

    bits_rx = bits_rx[:len(bits_tx)]

    errores = int(np.sum(bits_tx != bits_rx))
    ber = errores / len(bits_tx)

    return bits_rx.astype(np.uint8), {
        "padding_canal": padding_canal,
        "palabras_fuente_canal": int(U.shape[0]),
        "palabras_codigo_canal": int(V.shape[0]),
        "errores_bits_comprimidos": errores,
        "ber_bits_comprimidos": ber,
        **estadisticas,
    }


def ejecutar_opcional_2(
    ruta_imagen: str,
    orden: int,
    ebn0_db: float,
    carpeta_tablas: str = "src/resultados/tablas",
    carpeta_imagenes: str = "src/resultados/imagenes",
    carpeta_figuras: str = "src/resultados/figuras",
):
    """
    Ejecuta el opcional 2 completo:

        imagen -> Huffman -> canal codificado -> Huffman inverso -> imagen reconstruida
    """

    os.makedirs(carpeta_tablas, exist_ok=True)
    os.makedirs(carpeta_imagenes, exist_ok=True)
    os.makedirs(carpeta_figuras, exist_ok=True)

    print()
    print("=" * 100)
    print("OPCIONAL 2 - TRANSMISIÓN DE MENSAJE COMPRIMIDO")
    print("Orden Huffman = {} | Eb/N0 = {} dB".format(orden, ebn0_db))
    print("=" * 100)

    resultado_huffman = ejecutar_huffman_para_orden(
        ruta_imagen=ruta_imagen,
        orden=orden,
        carpeta_tablas=carpeta_tablas
    )

    imagen_original = resultado_huffman["imagen_binaria"]
    bits_imagen_original = resultado_huffman["bits_imagen"]
    bits_comprimidos = resultado_huffman["bits_codificados"]
    codigos = resultado_huffman["codigos"]
    cantidad_simbolos_esperada = len(resultado_huffman["simbolos"])
    cantidad_bits_originales = len(bits_imagen_original)
    shape_original = imagen_original.shape
    padding_fuente = resultado_huffman["padding"]

    bits_comprimidos_rx, stats_canal = transmitir_bits_por_canal(
        bits_tx=bits_comprimidos,
        ebn0_db=ebn0_db
    )

    print()
    print("Transmisión por canal")
    print("-" * 70)
    print("Bits comprimidos transmitidos:      {}".format(len(bits_comprimidos)))
    print("Padding canal agregado:             {}".format(stats_canal["padding_canal"]))
    print("Palabras fuente canal K={}:          {}".format(K, stats_canal["palabras_fuente_canal"]))
    print("Palabras código canal N={}:          {}".format(N, stats_canal["palabras_codigo_canal"]))
    print("Síndromes no nulos:                 {}".format(stats_canal["sindromes_no_nulos"]))
    print("Palabras corregidas:                {}".format(stats_canal["palabras_corregidas"]))
    print("Errores en bits comprimidos:        {}".format(stats_canal["errores_bits_comprimidos"]))
    print("BER sobre mensaje comprimido:       {:.8e}".format(stats_canal["ber_bits_comprimidos"]))

    simbolos_recuperados, errores_prefijo, buffer_final = decodificar_huffman_con_limite(
        bits_codificados=bits_comprimidos_rx,
        codigos=codigos,
        cantidad_simbolos_esperada=cantidad_simbolos_esperada
    )

    print()
    print("Decodificación Huffman")
    print("-" * 70)
    print("Símbolos esperados:                 {}".format(cantidad_simbolos_esperada))
    print("Símbolos recuperados:               {}".format(len(simbolos_recuperados)))
    print("Errores de prefijo Huffman:         {}".format(errores_prefijo))
    print("Buffer final no decodificado:       '{}'".format(buffer_final))
    print("Padding fuente original:            {}".format(padding_fuente))

    if len(simbolos_recuperados) < cantidad_simbolos_esperada:
        faltan = cantidad_simbolos_esperada - len(simbolos_recuperados)
        simbolos_recuperados = np.concatenate([
            simbolos_recuperados,
            np.zeros(faltan, dtype=int)
        ])

    if len(simbolos_recuperados) > cantidad_simbolos_esperada:
        simbolos_recuperados = simbolos_recuperados[:cantidad_simbolos_esperada]

    bits_fuente_recuperados_con_padding = simbolos_a_bits(
        simbolos=simbolos_recuperados,
        orden=orden
    )

    bits_imagen_recuperados = bits_fuente_recuperados_con_padding[:cantidad_bits_originales]

    errores_imagen = int(np.sum(bits_imagen_original != bits_imagen_recuperados))
    ber_imagen = errores_imagen / cantidad_bits_originales

    print()
    print("Recuperación de imagen")
    print("-" * 70)
    print("Errores en bits de imagen:          {}".format(errores_imagen))
    print("BER final de imagen:                {:.8e}".format(ber_imagen))

    nombre_imagen = "reconstruida_orden{}_EbN0_{}dB.tif".format(orden, ebn0_db)
    ruta_imagen_reconstruida = os.path.join(carpeta_imagenes, nombre_imagen)

    imagen_recuperada = guardar_imagen_binaria(
        bits=bits_imagen_recuperados,
        shape_original=shape_original,
        ruta_salida=ruta_imagen_reconstruida
    )

    nombre_comparacion = "comparacion_orden{}_EbN0_{}dB.png".format(orden, ebn0_db)
    ruta_comparacion = os.path.join(carpeta_figuras, nombre_comparacion)

    guardar_comparacion_imagenes(
        imagen_original=imagen_original,
        imagen_recuperada=imagen_recuperada,
        ruta_salida=ruta_comparacion,
        titulo="Orden {} - Eb/N0 = {} dB".format(orden, ebn0_db)
    )

    print()
    print("Imagen reconstruida guardada en:    {}".format(ruta_imagen_reconstruida))
    print("Comparación guardada en:            {}".format(ruta_comparacion))

    return {
        "orden": orden,
        "ebn0_db": ebn0_db,
        "ruta_imagen_reconstruida": ruta_imagen_reconstruida,
        "ruta_comparacion": ruta_comparacion,
        "errores_imagen": errores_imagen,
        "ber_imagen": ber_imagen,
        "errores_bits_comprimidos": stats_canal["errores_bits_comprimidos"],
        "ber_bits_comprimidos": stats_canal["ber_bits_comprimidos"],
        "errores_prefijo": errores_prefijo,
    }


def ejecutar_opcional_2_ordenes_2_y_3(
    ruta_imagen: str,
    ebn0_db: float = 7.0
):
    """
    Ejecuta el opcional 2 para orden 2 y orden 3.
    """

    resultado_orden2 = ejecutar_opcional_2(
        ruta_imagen=ruta_imagen,
        orden=2,
        ebn0_db=ebn0_db
    )

    resultado_orden3 = ejecutar_opcional_2(
        ruta_imagen=ruta_imagen,
        orden=3,
        ebn0_db=ebn0_db
    )

    return {
        "orden2": resultado_orden2,
        "orden3": resultado_orden3,
    }