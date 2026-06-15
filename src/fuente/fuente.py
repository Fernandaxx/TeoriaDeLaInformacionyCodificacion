"""
huffman_fuente_unico.py

Codificación de fuente con Huffman para el archivo "logo FI.tif".

Este archivo hace todo en un solo script:

1. Carga la imagen TIFF.
2. La convierte a fuente binaria: píxeles 0 y 1.
3. Agrupa los bits en bloques de orden 2 y orden 3.
4. Calcula las frecuencias y probabilidades de cada mensaje.
5. Construye el árbol de Huffman.
6. Genera el diccionario de códigos.
7. Codifica la imagen.
8. Calcula:
   - largo promedio por bloque,
   - largo promedio por bit de fuente,
   - entropía,
   - tasa de compresión.
9. Grafica resultados simples para comparar orden 2 y orden 3.

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
# 1. NODO DEL ÁRBOL DE HUFFMAN
# ============================================================

@dataclass(order=True)
class NodoHuffman:
    """
    Nodo para el árbol de Huffman.

    En C/C++ esto sería parecido a un struct con punteros:
        struct Nodo {
            int simbolo;
            int frecuencia;
            Nodo* izquierda;
            Nodo* derecha;
        };

    En Python usamos una clase. Los hijos izquierda/derecha pueden ser None
    si el nodo es una hoja.
    """

    frecuencia: int
    orden_heap: int = field(compare=True)
    simbolo: Optional[int] = field(default=None, compare=False)
    izquierda: Optional["NodoHuffman"] = field(default=None, compare=False)
    derecha: Optional["NodoHuffman"] = field(default=None, compare=False)


# ============================================================
# 2. CARGA Y BINARIZACIÓN DE LA IMAGEN
# ============================================================

def cargar_imagen_binaria(ruta_imagen: str, umbral: int = 127) -> np.ndarray:
    """
    Carga la imagen y la transforma en una secuencia binaria.

    La imagen se abre en escala de grises:
        negro cercano a 0
        blanco cercano a 255

    Luego hacemos:
        pixel > umbral  -> 1
        pixel <= umbral -> 0

    Devuelve un vector 1D de bits.

    Ejemplo:
        imagen =
        [[0, 255],
         [255, 0]]

        bits =
        [0, 1, 1, 0]
    """

    imagen = Image.open(ruta_imagen).convert("L")
    matriz = np.array(imagen, dtype=np.uint8)

    bits = (matriz > umbral).astype(np.uint8)

    return bits.ravel()


# ============================================================
# 3. AGRUPAMIENTO EN FUENTE EXTENDIDA DE ORDEN n
# ============================================================

def agrupar_bits(bits: np.ndarray, orden: int):
    """
    Agrupa la secuencia binaria en bloques no solapados de largo 'orden'.

    Para orden 2:
        bits = [1, 0, 0, 1, 1, 1]
        bloques = [[1, 0],
                   [0, 1],
                   [1, 1]]

    Para orden 3:
        bits = [1, 0, 0, 1, 1, 1]
        bloques = [[1, 0, 0],
                   [1, 1, 1]]

    Si la cantidad de bits no es múltiplo del orden, agregamos ceros al final.
    Eso se llama padding. Lo guardamos para saber cuántos bits agregamos.

    En vez de usar muchos for anidados como haríamos en C, usamos reshape de NumPy.
    """

    cantidad_bits = len(bits)
    resto = cantidad_bits % orden

    if resto == 0:
        padding = 0
    else:
        padding = orden - resto

    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

    bloques = bits.reshape(-1, orden)

    return bloques, padding


def bloques_a_decimal(bloques: np.ndarray, orden: int) -> np.ndarray:
    """
    Convierte cada bloque binario a decimal.

    Para orden 2:
        00 -> 0
        01 -> 1
        10 -> 2
        11 -> 3

    Para orden 3:
        000 -> 0
        001 -> 1
        010 -> 2
        ...
        111 -> 7

    Esto es útil porque el enunciado sugiere representar los mensajes
    de la fuente extendida en forma decimal.

    Vectorización:
        En C haríamos un for por cada bloque.
        En NumPy hacemos una multiplicación matricial.

    Ejemplo orden 3:
        bloque = [1, 0, 1]
        pesos = [4, 2, 1]
        decimal = 1*4 + 0*2 + 1*1 = 5
    """

    pesos = 2 ** np.arange(orden - 1, -1, -1)
    simbolos_decimales = bloques @ pesos

    return simbolos_decimales.astype(int)


def decimal_a_binario(simbolo: int, orden: int) -> str:
    """
    Convierte un símbolo decimal a string binario de largo fijo.

    Ejemplo:
        simbolo = 2, orden = 2 -> "10"
        simbolo = 5, orden = 3 -> "101"
    """

    return format(simbolo, f"0{orden}b")


# ============================================================
# 4. FRECUENCIAS Y PROBABILIDADES
# ============================================================

def calcular_frecuencias(simbolos: np.ndarray, orden: int) -> np.ndarray:
    """
    Calcula la frecuencia de cada símbolo posible.

    Para orden 2 hay 2^2 = 4 símbolos posibles.
    Para orden 3 hay 2^3 = 8 símbolos posibles.

    np.bincount cuenta cuántas veces aparece cada símbolo decimal.
    """

    cantidad_simbolos_posibles = 2 ** orden

    frecuencias = np.bincount(
        simbolos,
        minlength=cantidad_simbolos_posibles
    )

    return frecuencias


def imprimir_tabla_probabilidades(frecuencias: np.ndarray, codigos: dict, orden: int):
    """
    Imprime una tabla con:
        símbolo decimal,
        símbolo binario,
        frecuencia,
        probabilidad,
        código Huffman.
    """

    total = np.sum(frecuencias)

    print()
    print(f"Tabla de probabilidades y códigos - Orden {orden}")
    print("-" * 70)
    print(f"{'Decimal':<10} {'Binario':<10} {'Frecuencia':<12} {'Probabilidad':<15} {'Código Huffman'}")
    print("-" * 70)

    for simbolo, frecuencia in enumerate(frecuencias):
        probabilidad = frecuencia / total if total > 0 else 0

        if simbolo in codigos:
            codigo = codigos[simbolo]
        else:
            codigo = "-"

        print(
            f"{simbolo:<10} "
            f"{decimal_a_binario(simbolo, orden):<10} "
            f"{frecuencia:<12} "
            f"{probabilidad:<15.6f} "
            f"{codigo}"
        )


# ============================================================
# 5. CONSTRUCCIÓN DEL ÁRBOL DE HUFFMAN
# ============================================================

def construir_arbol_huffman(frecuencias: np.ndarray) -> NodoHuffman:
    """
    Construye el árbol de Huffman usando una cola de prioridad.

    Idea del algoritmo:
        1. Tomar los dos símbolos menos frecuentes.
        2. Unirlos en un nodo padre.
        3. La frecuencia del padre es la suma de las dos frecuencias.
        4. Repetir hasta que quede un solo nodo: la raíz.

    heapq en Python es parecido a una priority_queue en C++.
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
        raise ValueError("No hay símbolos con frecuencia positiva.")

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


def generar_codigos_huffman(nodo: NodoHuffman, prefijo: str = "") -> dict:
    """
    Recorre el árbol y genera el diccionario de códigos.

    Convención:
        rama izquierda -> agrega "0"
        rama derecha   -> agrega "1"

    Si llegamos a una hoja, guardamos el código.
    """

    if nodo.simbolo is not None:
        if prefijo == "":
            prefijo = "0"
        return {nodo.simbolo: prefijo}

    codigos = {}

    codigos.update(generar_codigos_huffman(nodo.izquierda, prefijo + "0"))
    codigos.update(generar_codigos_huffman(nodo.derecha, prefijo + "1"))

    return codigos


# ============================================================
# 6. CODIFICACIÓN DE LA SECUENCIA
# ============================================================

def codificar_secuencia(simbolos: np.ndarray, codigos: dict) -> str:
    """
    Codifica toda la secuencia usando el diccionario de Huffman.

    Por ejemplo:
        símbolos = [0, 3, 2]
        códigos = {0: "1", 3: "01", 2: "00"}

        secuencia codificada = "1" + "01" + "00" = "10100"
    """

    return "".join(codigos[int(simbolo)] for simbolo in simbolos)


# ============================================================
# 7. MÉTRICAS DE COMPRESIÓN
# ============================================================

def calcular_entropia(frecuencias: np.ndarray) -> float:
    """
    Calcula la entropía de la fuente extendida:

        H = - sum p_i log2(p_i)

    Esta entropía queda en bits por símbolo extendido.
    """

    total = np.sum(frecuencias)
    probabilidades = frecuencias / total

    probabilidades_no_nulas = probabilidades[probabilidades > 0]

    entropia = -np.sum(probabilidades_no_nulas * np.log2(probabilidades_no_nulas))

    return float(entropia)


def calcular_largo_promedio(frecuencias: np.ndarray, codigos: dict) -> float:
    """
    Calcula el largo promedio del código de Huffman:

        L = sum p_i * l_i

    donde:
        p_i = probabilidad del símbolo i
        l_i = longitud del código Huffman del símbolo i

    Este largo promedio queda en bits codificados por símbolo extendido.
    """

    total = np.sum(frecuencias)
    largo_promedio = 0.0

    for simbolo, frecuencia in enumerate(frecuencias):
        if frecuencia > 0:
            p = frecuencia / total
            largo_codigo = len(codigos[simbolo])
            largo_promedio += p * largo_codigo

    return float(largo_promedio)


def calcular_metricas(frecuencias: np.ndarray, codigos: dict, orden: int, longitud_codificada: int):
    """
    Calcula las métricas principales del TP.

    largo_promedio_bloque:
        bits Huffman promedio por símbolo extendido.
        Ejemplo: para orden 2, por cada bloque tipo 00, 01, 10, 11.

    largo_promedio_bit:
        bits Huffman promedio por bit original de la fuente.
        Se calcula dividiendo por el orden.

    tasa_compresion:
        longitud sin comprimir / longitud comprimida.

        Como la fuente es binaria:
            cada bloque de orden n tiene n bits originales.

        Entonces:
            tasa = orden / largo_promedio_bloque

        Si tasa > 1, hay compresión.
    """

    total_bloques = np.sum(frecuencias)

    entropia_bloque = calcular_entropia(frecuencias)
    largo_promedio_bloque = calcular_largo_promedio(frecuencias, codigos)

    largo_promedio_bit = largo_promedio_bloque / orden
    entropia_por_bit = entropia_bloque / orden

    longitud_original = total_bloques * orden
    tasa_compresion = longitud_original / longitud_codificada

    eficiencia = entropia_bloque / largo_promedio_bloque

    return {
        "total_bloques": int(total_bloques),
        "longitud_original": int(longitud_original),
        "longitud_codificada": int(longitud_codificada),
        "entropia_bloque": entropia_bloque,
        "entropia_por_bit": entropia_por_bit,
        "largo_promedio_bloque": largo_promedio_bloque,
        "largo_promedio_bit": largo_promedio_bit,
        "tasa_compresion": tasa_compresion,
        "eficiencia": eficiencia,
    }


# ============================================================
# 8. ANÁLISIS COMPLETO PARA UN ORDEN
# ============================================================

def analizar_orden(bits: np.ndarray, orden: int):
    """
    Ejecuta todo el análisis para un orden determinado.

    Para este TP vamos a llamar esta función con:
        orden = 2
        orden = 3
    """

    bloques, padding = agrupar_bits(bits, orden)
    simbolos = bloques_a_decimal(bloques, orden)

    frecuencias = calcular_frecuencias(simbolos, orden)

    arbol = construir_arbol_huffman(frecuencias)
    codigos = generar_codigos_huffman(arbol)

    secuencia_codificada = codificar_secuencia(simbolos, codigos)

    metricas = calcular_metricas(
        frecuencias=frecuencias,
        codigos=codigos,
        orden=orden,
        longitud_codificada=len(secuencia_codificada)
    )

    return {
        "orden": orden,
        "padding": padding,
        "frecuencias": frecuencias,
        "codigos": codigos,
        "secuencia_codificada": secuencia_codificada,
        "metricas": metricas,
    }


# ============================================================
# 9. GRÁFICO SIMPLE
# ============================================================

def graficar_resultados(resultados):
    """
    Grafica comparación entre orden 2 y orden 3.

    No es obligatorio, pero sirve para visualizar rápido:
        - largo promedio por bit,
        - tasa de compresión.
    """

    ordenes = [r["orden"] for r in resultados]
    largos_por_bit = [r["metricas"]["largo_promedio_bit"] for r in resultados]
    tasas = [r["metricas"]["tasa_compresion"] for r in resultados]

    plt.figure(figsize=(8, 5))
    plt.plot(ordenes, largos_por_bit, marker="o", label="Largo promedio por bit")
    plt.plot(ordenes, tasas, marker="o", label="Tasa de compresión")
    plt.xlabel("Orden de la fuente extendida")
    plt.ylabel("Valor")
    plt.title("Compresión Huffman - Fuente extendida")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados_huffman_fuente.png", dpi=300)
    plt.show()


# ============================================================
# 10. PROGRAMA PRINCIPAL
# ============================================================

def main():
    """
    Programa principal.

    Antes de ejecutar:
        1. Guardá este archivo como huffman_fuente_unico.py.
        2. Colocá "logo FI.tif" en la misma carpeta.
        3. Ejecutá:
              python huffman_fuente_unico.py
    """

    ruta_imagen = "/Users/fernandaavila/Documents/GitHub/TeoriaDeLaInformacionyCodificacion/data/logo FI.tif"

    print("Cargando imagen...")
    bits = cargar_imagen_binaria(ruta_imagen)

    print(f"Cantidad de bits originales de la imagen: {len(bits)}")
    print(f"Cantidad de ceros: {np.sum(bits == 0)}")
    print(f"Cantidad de unos:  {np.sum(bits == 1)}")

    resultados = []

    for orden in [2, 3]:
        print()
        print("=" * 80)
        print(f"ANÁLISIS PARA FUENTE EXTENDIDA DE ORDEN {orden}")
        print("=" * 80)

        resultado = analizar_orden(bits, orden)
        resultados.append(resultado)

        imprimir_tabla_probabilidades(
            frecuencias=resultado["frecuencias"],
            codigos=resultado["codigos"],
            orden=orden
        )

        metricas = resultado["metricas"]

        print()
        print(f"Resumen orden {orden}")
        print("-" * 50)
        print(f"Bits de padding agregados:              {resultado['padding']}")
        print(f"Cantidad de bloques:                    {metricas['total_bloques']}")
        print(f"Longitud original considerada [bits]:   {metricas['longitud_original']}")
        print(f"Longitud codificada [bits]:             {metricas['longitud_codificada']}")
        print(f"Entropía por bloque [bits/bloque]:      {metricas['entropia_bloque']:.6f}")
        print(f"Entropía por bit [bits/bit fuente]:     {metricas['entropia_por_bit']:.6f}")
        print(f"Largo promedio por bloque [bits]:       {metricas['largo_promedio_bloque']:.6f}")
        print(f"Largo promedio por bit fuente [bits]:   {metricas['largo_promedio_bit']:.6f}")
        print(f"Tasa de compresión:                     {metricas['tasa_compresion']:.6f}")
        print(f"Eficiencia Huffman:                     {metricas['eficiencia']:.6f}")

        print()
        print("Primeros 100 bits de la secuencia codificada:")
        print(resultado["secuencia_codificada"][:100])

    print()
    print("=" * 80)
    print("COMPARACIÓN FINAL")
    print("=" * 80)
    print(f"{'Orden':<8} {'L prom/bloque':<18} {'L prom/bit':<15} {'Tasa comp.':<15} {'Eficiencia':<12}")
    print("-" * 80)

    for r in resultados:
        orden = r["orden"]
        m = r["metricas"]
        print(
            f"{orden:<8} "
            f"{m['largo_promedio_bloque']:<18.6f} "
            f"{m['largo_promedio_bit']:<15.6f} "
            f"{m['tasa_compresion']:<15.6f} "
            f"{m['eficiencia']:<12.6f}"
        )

    graficar_resultados(resultados)


if __name__ == "__main__":
    main()