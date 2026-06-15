"""
opcional2_huffman_canal.py

Opcional 2:
1. Comprime la imagen "logo FI.tif" con Huffman.
2. Transmite el mensaje comprimido por canal AWGN con BPSK.
3. Usa código de bloque lineal (14,10) como corrector.
4. Decodifica Huffman.
5. Recupera y guarda la imagen reconstruida.

Requisitos:
    pip install numpy pillow matplotlib
"""

import heapq
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RUTA_IMAGEN = "/Users/fernandaavila/Documents/GitHub/TeoriaDeLaInformacionyCodificacion/src/fuente/logo FI.tif"

# Probá primero con Eb/N0 alto para que la imagen se recupere bien.
# Después podés bajarlo para ver cómo se degrada.
EBN0_DB = 7.0

# Código de canal (14,10)
K = 10
N = 14


# ============================================================
# 1. HUFFMAN
# ============================================================

@dataclass(order=True)
class NodoHuffman:
    frecuencia: int
    orden_heap: int = field(compare=True)
    simbolo: Optional[int] = field(default=None, compare=False)
    izquierda: Optional["NodoHuffman"] = field(default=None, compare=False)
    derecha: Optional["NodoHuffman"] = field(default=None, compare=False)


def cargar_imagen_binaria(ruta_imagen: str, umbral: int = 127):
    """
    Carga la imagen en escala de grises y la convierte a bits 0/1.

    Negro -> 0
    Blanco -> 1
    """

    imagen = Image.open(ruta_imagen).convert("L")
    matriz_gris = np.array(imagen, dtype=np.uint8)

    matriz_binaria = (matriz_gris > umbral).astype(np.uint8)
    bits = matriz_binaria.ravel()

    return matriz_binaria, bits


def agrupar_bits(bits: np.ndarray, orden: int):
    """
    Agrupa los bits en bloques de longitud 'orden'.

    Ejemplo orden 3:
        [1, 0, 1, 0, 0, 1] -> [[1,0,1], [0,0,1]]

    Si falta algún bit para completar el último bloque, agrega ceros.
    """

    resto = len(bits) % orden

    if resto == 0:
        padding = 0
    else:
        padding = orden - resto

    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

    bloques = bits.reshape(-1, orden)

    return bloques, padding


def bloques_a_decimal(bloques: np.ndarray, orden: int):
    """
    Convierte bloques binarios a representación decimal.

    Orden 2:
        00 -> 0
        01 -> 1
        10 -> 2
        11 -> 3

    Orden 3:
        000 -> 0
        001 -> 1
        ...
        111 -> 7

    Esto está vectorizado con NumPy. En C lo haríamos con un for;
    acá usamos producto matricial.
    """

    pesos = 2 ** np.arange(orden - 1, -1, -1)
    simbolos = bloques @ pesos

    return simbolos.astype(int)


def simbolos_a_bits(simbolos: np.ndarray, orden: int):
    """
    Convierte símbolos decimales otra vez a bloques binarios.
    """

    if len(simbolos) == 0:
        return np.array([], dtype=np.uint8)

    desplazamientos = np.arange(orden - 1, -1, -1)
    bits = ((simbolos[:, None] >> desplazamientos) & 1).astype(np.uint8)

    return bits.reshape(-1)


def calcular_frecuencias(simbolos: np.ndarray, orden: int):
    """
    Cuenta cuántas veces aparece cada símbolo de la fuente extendida.
    """

    cantidad_simbolos_posibles = 2 ** orden

    frecuencias = np.bincount(
        simbolos,
        minlength=cantidad_simbolos_posibles
    )

    return frecuencias


def construir_arbol_huffman(frecuencias: np.ndarray):
    """
    Construye el árbol de Huffman usando heapq.

    heapq funciona como una cola de prioridad:
    siempre saco los dos nodos de menor frecuencia.
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
        símbolo -> código Huffman
    """

    if nodo.simbolo is not None:
        if prefijo == "":
            prefijo = "0"
        return {nodo.simbolo: prefijo}

    codigos = {}
    codigos.update(generar_codigos_huffman(nodo.izquierda, prefijo + "0"))
    codigos.update(generar_codigos_huffman(nodo.derecha, prefijo + "1"))

    return codigos


def codificar_huffman(simbolos: np.ndarray, codigos: dict):
    """
    Convierte la secuencia de símbolos en una secuencia binaria comprimida.
    """

    cadena = "".join(codigos[int(s)] for s in simbolos)
    bits = np.fromiter((int(b) for b in cadena), dtype=np.uint8)

    return bits


def preparar_decodificador_huffman(codigos: dict):
    """
    Arma:
        código Huffman -> símbolo

    También arma el conjunto de prefijos válidos para detectar errores
    de sincronismo.
    """

    decodificador = {codigo: simbolo for simbolo, codigo in codigos.items()}

    prefijos = set()
    for codigo in decodificador.keys():
        for i in range(1, len(codigo)):
            prefijos.add(codigo[:i])

    return decodificador, prefijos


def decodificar_huffman(bits: np.ndarray, codigos: dict, cantidad_simbolos_esperada: int):
    """
    Decodifica una secuencia binaria comprimida usando el diccionario Huffman.

    Como Huffman es de longitud variable, si queda algún error de canal
    puede desincronizar la decodificación.
    """

    decodificador, prefijos = preparar_decodificador_huffman(codigos)

    buffer = ""
    simbolos_decodificados = []
    errores_prefijo = 0

    for bit in bits:
        buffer += str(int(bit))

        if buffer in decodificador:
            simbolos_decodificados.append(decodificador[buffer])
            buffer = ""

            if len(simbolos_decodificados) == cantidad_simbolos_esperada:
                break

        elif buffer not in prefijos:
            # Llegamos a una combinación que no corresponde a ningún código
            # ni prefijo válido. Esto puede pasar si quedó un error de canal.
            errores_prefijo += 1
            buffer = ""

    return np.array(simbolos_decodificados, dtype=int), errores_prefijo, buffer


def calcular_metricas_huffman(frecuencias: np.ndarray, codigos: dict, orden: int, longitud_codificada: int):
    """
    Calcula largo promedio, entropía y tasa de compresión.
    """

    total = np.sum(frecuencias)
    probabilidades = frecuencias / total

    largo_promedio_bloque = 0.0
    entropia_bloque = 0.0

    for simbolo, p in enumerate(probabilidades):
        if p > 0:
            largo_promedio_bloque += p * len(codigos[simbolo])
            entropia_bloque -= p * np.log2(p)

    largo_promedio_bit = largo_promedio_bloque / orden

    longitud_original = int(total * orden)
    tasa_compresion = longitud_original / longitud_codificada

    return {
        "largo_promedio_bloque": largo_promedio_bloque,
        "largo_promedio_bit": largo_promedio_bit,
        "entropia_bloque": entropia_bloque,
        "entropia_bit": entropia_bloque / orden,
        "longitud_original": longitud_original,
        "longitud_codificada": longitud_codificada,
        "tasa_compresion": tasa_compresion,
    }


# ============================================================
# 2. CÓDIGO DE CANAL (14,10)
# ============================================================

def crear_matrices_codigo_14_10():
    """
    Matriz generadora sistemática:
        G = [I_k | P]

    Matriz de control de paridad:
        H = [P^T | I_{n-k}]

    Si vos usás otra P en tu Ejercicio 1, reemplazá esta matriz P.
    """

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

    I_k = np.eye(K, dtype=np.uint8)
    I_r = np.eye(N - K, dtype=np.uint8)

    G = np.concatenate([I_k, P], axis=1)
    H = np.concatenate([P.T, I_r], axis=1)

    return G, H


def completar_multiplo(bits: np.ndarray, multiplo: int):
    """
    Agrega ceros al final para que la longitud sea múltiplo de 'multiplo'.
    """

    resto = len(bits) % multiplo

    if resto == 0:
        padding = 0
    else:
        padding = multiplo - resto

    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

    return bits, padding


def codificar_canal(U: np.ndarray, G: np.ndarray):
    """
    Codifica con:
        V = U G mod 2

    U tiene filas de 10 bits.
    V tiene filas de 14 bits.

    Esto es lo mismo que haríamos en C con bucles, pero vectorizado.
    """

    V = (U @ G) % 2
    return V.astype(np.uint8)

def canal_awgn_bpsk(V: np.ndarray, ebn0_db: float, amplitud: float = 1.0):
    """
    Canal AWGN con BPSK y detección dura.

    IMPORTANTE:
    V viene como uint8, con valores 0 y 1.
    Antes de hacer (2*V - 1), lo convertimos a float para evitar overflow.

    BPSK:
        bit 0 -> -A
        bit 1 -> +A
    """

    ebn0_lineal = 10 ** (ebn0_db / 10)

    Es = amplitud ** 2
    Ebf = Es * N / K
    N0 = Ebf / ebn0_lineal

    # Corrección importante:
    # Convertimos V a float antes de hacer 2*V - 1.
    V_float = V.astype(float)

    S = (2 * V_float - 1) * amplitud

    ruido = np.sqrt(N0 / 2) * (
        np.random.randn(*S.shape) + 1j * np.random.randn(*S.shape)
    )

    R = S + ruido

    R_bits = (np.real(R) > 0).astype(np.uint8)

    return R_bits


def corregir_por_sindrome(R_bits: np.ndarray, H: np.ndarray):
    """
    Corrección por síndrome.

    Se calcula:
        S = R H^T mod 2

    Si el síndrome coincide con una columna de H, se invierte ese bit.
    """

    V_corr = R_bits.copy()

    sindromes = (R_bits @ H.T) % 2

    # Mapa: síndrome -> posición del bit a corregir
    mapa_sindromes = {}

    for posicion, columna in enumerate(H.T):
        mapa_sindromes[tuple(columna)] = posicion

    cantidad_sindromes_no_nulos = 0
    cantidad_corregidos = 0
    cantidad_no_corregidos = 0

    for fila in range(sindromes.shape[0]):
        s = tuple(sindromes[fila])

        if any(s):
            cantidad_sindromes_no_nulos += 1

            if s in mapa_sindromes:
                posicion_error = mapa_sindromes[s]
                V_corr[fila, posicion_error] ^= 1
                cantidad_corregidos += 1
            else:
                cantidad_no_corregidos += 1

    estadisticas = {
        "sindromes_no_nulos": cantidad_sindromes_no_nulos,
        "palabras_corregidas": cantidad_corregidos,
        "sindromes_no_corregidos": cantidad_no_corregidos,
    }

    return V_corr, estadisticas


def decodificar_canal_sistematico(V_corr: np.ndarray):
    """
    Como G es sistemática, la palabra de fuente estimada está
    en las primeras K columnas.
    """

    return V_corr[:, :K]


# ============================================================
# 3. RECONSTRUCCIÓN DE IMAGEN
# ============================================================

def guardar_imagen_binaria(bits: np.ndarray, shape_original, nombre_salida: str):
    """
    Reconstruye una imagen 0/255 a partir de bits 0/1.
    """

    matriz = bits.reshape(shape_original)
    imagen_uint8 = (matriz * 255).astype(np.uint8)

    Image.fromarray(imagen_uint8).save(nombre_salida)

    return imagen_uint8


def guardar_comparacion(imagen_original, imagen_recuperada, nombre_salida: str, titulo: str):
    """
    Guarda una figura comparando imagen original e imagen recuperada.
    """

    plt.figure(figsize=(8, 4))

    plt.subplot(1, 2, 1)
    plt.imshow(imagen_original * 255, cmap="gray")
    plt.title("Original binaria")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(imagen_recuperada, cmap="gray")
    plt.title("Recuperada")
    plt.axis("off")

    plt.suptitle(titulo)
    plt.tight_layout()
    plt.savefig(nombre_salida, dpi=300)
    plt.show()


# ============================================================
# 4. OPCIONAL 2 COMPLETO
# ============================================================

def ejecutar_opcional_2(orden: int, ebn0_db: float):
    """
    Ejecuta el flujo completo:

        imagen -> Huffman -> canal codificado -> Huffman inverso -> imagen
    """

    print()
    print("=" * 90)
    print(f"OPCIONAL 2 - ORDEN {orden} - Eb/N0 = {ebn0_db} dB")
    print("=" * 90)

    # --------------------------------------------------------
    # A. Cargar imagen y comprimir con Huffman
    # --------------------------------------------------------

    imagen_binaria, bits_imagen = cargar_imagen_binaria(RUTA_IMAGEN)
    shape_original = imagen_binaria.shape
    cantidad_bits_originales = len(bits_imagen)

    bloques, padding_fuente = agrupar_bits(bits_imagen, orden)
    simbolos = bloques_a_decimal(bloques, orden)

    frecuencias = calcular_frecuencias(simbolos, orden)
    arbol = construir_arbol_huffman(frecuencias)
    codigos = generar_codigos_huffman(arbol)

    bits_comprimidos = codificar_huffman(simbolos, codigos)

    metricas = calcular_metricas_huffman(
        frecuencias=frecuencias,
        codigos=codigos,
        orden=orden,
        longitud_codificada=len(bits_comprimidos)
    )

    print()
    print("Compresión Huffman")
    print("-" * 50)
    print(f"Bits originales de imagen:          {cantidad_bits_originales}")
    print(f"Padding fuente agregado:            {padding_fuente}")
    print(f"Cantidad de símbolos Huffman:       {len(simbolos)}")
    print(f"Longitud comprimida [bits]:         {len(bits_comprimidos)}")
    print(f"Largo promedio por bloque:          {metricas['largo_promedio_bloque']:.6f}")
    print(f"Largo promedio por bit de fuente:   {metricas['largo_promedio_bit']:.6f}")
    print(f"Tasa de compresión:                 {metricas['tasa_compresion']:.6f}")

    print()
    print("Diccionario Huffman")
    print("-" * 50)
    for simbolo in sorted(codigos.keys()):
        binario = format(simbolo, f"0{orden}b")
        print(f"m{simbolo} = {binario} -> {codigos[simbolo]}")

    # --------------------------------------------------------
    # B. Preparar bits comprimidos para código de canal
    # --------------------------------------------------------

    bits_tx_canal, padding_canal = completar_multiplo(bits_comprimidos, K)

    U = bits_tx_canal.reshape(-1, K)

    G, H = crear_matrices_codigo_14_10()

    V = codificar_canal(U, G)

    # --------------------------------------------------------
    # C. Transmisión por canal AWGN + BPSK
    # --------------------------------------------------------

    R_bits = canal_awgn_bpsk(V, ebn0_db=ebn0_db)

    # --------------------------------------------------------
    # D. Corrección por síndrome y decodificación de canal
    # --------------------------------------------------------

    V_corr, stats_correccion = corregir_por_sindrome(R_bits, H)
    U_estimada = decodificar_canal_sistematico(V_corr)

    bits_rx_canal = U_estimada.reshape(-1)

    # Sacamos el padding que agregamos solo para armar bloques de 10 bits.
    if padding_canal > 0:
        bits_comprimidos_recibidos = bits_rx_canal[:-padding_canal]
    else:
        bits_comprimidos_recibidos = bits_rx_canal

    # Nos aseguramos de comparar misma longitud.
    bits_comprimidos_recibidos = bits_comprimidos_recibidos[:len(bits_comprimidos)]

    errores_bits_comprimidos = np.sum(bits_comprimidos != bits_comprimidos_recibidos)
    ber_comprimido = errores_bits_comprimidos / len(bits_comprimidos)

    print()
    print("Transmisión por canal")
    print("-" * 50)
    print(f"Bits comprimidos transmitidos:      {len(bits_comprimidos)}")
    print(f"Padding canal agregado:             {padding_canal}")
    print(f"Palabras de fuente canal, K=10:     {U.shape[0]}")
    print(f"Palabras de código canal, N=14:     {V.shape[0]}")
    print(f"Síndromes no nulos:                 {stats_correccion['sindromes_no_nulos']}")
    print(f"Palabras corregidas:                {stats_correccion['palabras_corregidas']}")
    print(f"Síndromes no corregidos:            {stats_correccion['sindromes_no_corregidos']}")
    print(f"Errores en bits comprimidos:        {errores_bits_comprimidos}")
    print(f"BER sobre mensaje comprimido:       {ber_comprimido:.8e}")

    # --------------------------------------------------------
    # E. Decodificación Huffman
    # --------------------------------------------------------

    simbolos_recuperados, errores_prefijo, buffer_final = decodificar_huffman(
        bits=bits_comprimidos_recibidos,
        codigos=codigos,
        cantidad_simbolos_esperada=len(simbolos)
    )

    print()
    print("Decodificación Huffman")
    print("-" * 50)
    print(f"Símbolos esperados:                 {len(simbolos)}")
    print(f"Símbolos recuperados:               {len(simbolos_recuperados)}")
    print(f"Errores de prefijo Huffman:         {errores_prefijo}")
    print(f"Buffer final no decodificado:       '{buffer_final}'")

    # Si por errores de canal se recuperaron menos símbolos, completamos con ceros
    # para poder reconstruir una imagen y visualizar el daño.
    if len(simbolos_recuperados) < len(simbolos):
        faltan = len(simbolos) - len(simbolos_recuperados)
        simbolos_recuperados = np.concatenate([
            simbolos_recuperados,
            np.zeros(faltan, dtype=int)
        ])

    if len(simbolos_recuperados) > len(simbolos):
        simbolos_recuperados = simbolos_recuperados[:len(simbolos)]

    bits_fuente_recuperados_con_padding = simbolos_a_bits(simbolos_recuperados, orden)

    # Sacamos padding de fuente y nos quedamos con la cantidad original de bits.
    bits_imagen_recuperados = bits_fuente_recuperados_con_padding[:cantidad_bits_originales]

    # --------------------------------------------------------
    # F. Comparación con imagen original
    # --------------------------------------------------------

    errores_imagen = np.sum(bits_imagen != bits_imagen_recuperados)
    ber_imagen = errores_imagen / cantidad_bits_originales

    print()
    print("Recuperación de imagen")
    print("-" * 50)
    print(f"Errores en bits de imagen:          {errores_imagen}")
    print(f"BER final de imagen:                {ber_imagen:.8e}")

    nombre_imagen = f"reconstruida_orden{orden}_EbN0_{ebn0_db}dB.tif"
    imagen_recuperada = guardar_imagen_binaria(
        bits=bits_imagen_recuperados,
        shape_original=shape_original,
        nombre_salida=nombre_imagen
    )

    nombre_comparacion = f"comparacion_orden{orden}_EbN0_{ebn0_db}dB.png"
    guardar_comparacion(
        imagen_original=imagen_binaria,
        imagen_recuperada=imagen_recuperada,
        nombre_salida=nombre_comparacion,
        titulo=f"Orden {orden} - Eb/N0 = {ebn0_db} dB"
    )

    print()
    print(f"Imagen recuperada guardada como:    {nombre_imagen}")
    print(f"Comparación guardada como:          {nombre_comparacion}")


# ============================================================
# 5. MAIN
# ============================================================

def main():
    np.random.seed(1)

    ejecutar_opcional_2(orden=2, ebn0_db=EBN0_DB)
    ejecutar_opcional_2(orden=3, ebn0_db=EBN0_DB)


if __name__ == "__main__":
    main()