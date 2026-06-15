import numpy as np
from itertools import combinations


# ============================================================
# BLOQUE 0 - FUENTE: genera U
# ============================================================

def generar_fuente(num_palabras: int, k: int) -> np.ndarray:
    """
    Genera la matriz U.
    Cada fila es una palabra de fuente de largo k.
    Dimensión: U = num_palabras x k
    """
    U = np.random.randint(0, 2, size=(num_palabras, k), dtype=np.uint8)
    return U


# ============================================================
# BLOQUE 1 - CODIFICADOR: U -> V
# ============================================================

def generar_matriz_generadora(k: int, n: int) -> np.ndarray:
    """
    Genera la matriz generadora sistemática G = [I_k | P].
    Para este trabajo usamos un código (14,10), entonces P es de 10 x 4.
    """
    if k != 10 or n != 14:
        raise ValueError("Esta matriz P está definida para el código (14,10).")

    I_k = np.eye(k, dtype=np.uint8)

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

    G = np.concatenate((I_k, P), axis=1)

    return G


def codificar(U: np.ndarray, G: np.ndarray) -> np.ndarray:
    """
    COD:
    Entra U.
    Sale V = U @ G mod 2.
    """
    V = (U @ G) % 2
    return V.astype(np.uint8)


# ============================================================
# MATRIZ VERIFICADORA DE PARIDAD
# ============================================================

def generar_matriz_verificadora_de_paridad(G: np.ndarray) -> np.ndarray:
    """
    Si G = [I_k | P], entonces H = [P.T | I_(n-k)].

    H tiene dimensión:
        (n-k) x n

    Para calcular síndromes de muchas palabras:
        S = R @ H.T mod 2
    """
    k, n = G.shape

    P = G[:, k:]
    I_paridad = np.eye(n - k, dtype=np.uint8)

    H = np.concatenate((P.T, I_paridad), axis=1)

    return H.astype(np.uint8)


def verificar_palabras_codigo(V: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Verifica que las palabras V sean palabras válidas del código.

    Si V es una matriz de palabras de código, entonces:
        S = V @ H.T mod 2

    debe dar todo cero.
    """
    S = (V @ H.T) % 2
    return S.astype(np.uint8)


# ============================================================
# BLOQUE 2 - CANAL AWGN + BPSK: V -> R
# ============================================================

def canal_awgn_bpsk(V: np.ndarray, A: float, n: int, k: int, EbfN0_db: float):
    """
    CANAL:
    Entra V.
    Modula BPSK, agrega ruido AWGN y aplica detección dura.

    Sale:
        R: matriz binaria recibida después de la detección dura.
        r: matriz recibida analógica antes del decisor.
        N0: densidad espectral de ruido usada.
    """

    EbfN0_lineal = 10 ** (EbfN0_db / 10)

    Es = A ** 2
    Ebf = Es * (n / k) #Ec = Es 
    N0 = Ebf / EbfN0_lineal

    # BPSK:
    # bit 0 -> -A
    # bit 1 -> +A
   
    s = (2 * V.astype(float) - 1) * A

    ruido_real = np.random.randn(*V.shape)
    ruido_imag = np.random.randn(*V.shape)

    noise = np.sqrt(N0 / 2) * (ruido_real + 1j * ruido_imag)

    r = s + noise

    # Detección dura:
    # si real(r) > 0 decide 1
    # si real(r) <= 0 decide 0
    R = (r.real > 0).astype(np.uint8)

    return R, r, N0


# ============================================================
# CÁLCULO DE d_min
# ============================================================

def calcular_dmin(G: np.ndarray, k: int) -> int:
    """
    Calcula la distancia mínima d_min del código.

    Genera todas las palabras posibles de fuente, excepto la nula.
    Para k = 10 son 1023 palabras, así que este for está bien.
    """
    d_min = None

    for i in range(1, 2 ** k):
        u = np.array(list(np.binary_repr(i, width=k)), dtype=np.uint8)

        v = (u @ G) % 2

        peso = int(np.sum(v))

        if d_min is None or peso < d_min:
            d_min = peso

    return int(d_min)




# ============================================================
# BLOQUE 3 - DETECTOR / CORRECTOR: R -> V_e
# ============================================================

def calcular_sindromes(R: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Calcula la matriz de síndromes:

        S = R @ H.T mod 2

    Entra:
        R: matriz recibida, dimensión num_palabras x n.

    Sale:
        S: matriz de síndromes, dimensión num_palabras x (n-k).
    """
    S = (R @ H.T) % 2
    return S.astype(np.uint8)


def generar_tabla_sindromes(H: np.ndarray, t: int) -> dict:
    """
    Genera una tabla:
        síndrome -> patrón de error

    Se usa en modo corrector.
    Si d_min = 3, entonces t = 1.
    Por lo tanto se corrigen errores de un solo bit.
    """
    n = H.shape[1]

    tabla = {}

    for peso in range(1, t + 1):
        for indices in combinations(range(n), peso):

            e = np.zeros(n, dtype=np.uint8)
            e[list(indices)] = 1

            sindrome = (e @ H.T) % 2

            tabla[tuple(sindrome)] = e

    return tabla



def detector_corrector(R: np.ndarray, H: np.ndarray, d_min: int, modo: str):
    """
    DET/CORR:
    Entra R.
    Calcula S = R @ H.T mod 2.
    Sale V_e.

    modo = "corrector":
        intenta corregir usando tabla de síndromes.
        V_e conserva la misma cantidad de filas que R.

    modo = "detector":
        descarta las palabras con síndrome no nulo.
        V_e puede tener menos filas que R.
    """

    if modo not in ["corrector", "detector"]:
        raise ValueError("modo debe ser 'corrector' o 'detector'.")

    S = calcular_sindromes(R, H)

    sindrome_cero = np.all(S == 0, axis=1)

    if modo == "corrector":

        t = (d_min - 1) // 2

        tabla = generar_tabla_sindromes(H, t)

        V_e = R.copy()

        # Recorremos la tabla de síndromes.
        # No recorremos palabra por palabra.
        # Cada máscara selecciona todas las filas con el mismo síndrome.
        for sindrome, error_estimado in tabla.items():

            mascara = np.all(S == np.array(sindrome, dtype=np.uint8), axis=1)

            V_e[mascara] = (V_e[mascara] + error_estimado) % 2

        filas_aceptadas = np.ones(R.shape[0], dtype=bool)

    else:

        # En modo detector, las palabras con síndrome no nulo se descartan.
        filas_aceptadas = sindrome_cero

        V_e = R[filas_aceptadas].copy()

    return V_e.astype(np.uint8), S, filas_aceptadas


# ============================================================
# BLOQUE 4 - DECODIFICADOR: V_e -> U_e
# ============================================================

def decodificar(V_e: np.ndarray, k: int) -> np.ndarray:
    """
    DEC:
    Entra V_e.
    Sale U_e.

    Como el código es sistemático G = [I | P],
    los primeros k bits son los bits de fuente.
    """
    U_e = V_e[:, :k]

    return U_e.astype(np.uint8)


# ============================================================
# CÁLCULO DE ERRORES
# ============================================================

def calcular_metricas(U: np.ndarray, U_e: np.ndarray, filas_aceptadas: np.ndarray, modo: str) -> dict:
    """
    Calcula P_ep y P_eb.

    En corrector:
        se comparan todas las filas.

    En detector:
        se comparan solo las filas aceptadas,
        porque las palabras detectadas como erróneas fueron descartadas.
    """

    U_ref = U[filas_aceptadas]

    total_palabras_comparadas = U_ref.shape[0]
    k = U.shape[1]

    if total_palabras_comparadas == 0:
        return {
            "palabras_comparadas": 0,
            "palabras_descartadas": int(U.shape[0]),
            "errores_palabra": 0,
            "errores_bit": 0,
            "Pep": np.nan,
            "Peb": np.nan,
            "P_descartadas": 1.0,
            "P_error_no_detectado_sobre_total": 0.0,
        }

    E = (U_e != U_ref)

    errores_palabra = int(np.sum(np.any(E, axis=1)))
    errores_bit = int(np.sum(E))

    Pep = errores_palabra / total_palabras_comparadas
    Peb = errores_bit / (total_palabras_comparadas * k)

    palabras_descartadas = int(U.shape[0] - total_palabras_comparadas)

    return {
        "palabras_comparadas": int(total_palabras_comparadas),
        "palabras_descartadas": palabras_descartadas,
        "errores_palabra": errores_palabra,
        "errores_bit": errores_bit,
        "Pep": Pep,
        "Peb": Peb,
        "P_descartadas": palabras_descartadas / U.shape[0],
        "P_error_no_detectado_sobre_total": errores_palabra / U.shape[0],
    }


# ============================================================
# FUNCIONES PARA MOSTRAR EL FLUJO
# ============================================================

def imprimir_bloque(titulo: str):
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)


def imprimir_matriz(nombre: str, M: np.ndarray, max_filas: int = 10):
    print(f"{nombre}: shape = {M.shape}")

    if M.shape[0] <= max_filas:
        print(M)
    else:
        print(M[:max_filas])
        print(f"... se muestran las primeras {max_filas} filas de {M.shape[0]}")

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    np.random.seed(7)

    # Parámetros generales
    k = 10
    n = 14
    num_palabras = 10

    # Parámetros del canal
    A = 1.0
    EbfN0_db = 4.0

    # Elegir modo:
    # modo = "corrector"
    # modo = "detector"
    modo = "corrector"

    imprimir_bloque("CONFIGURACIÓN")
    print(f"Código lineal: ({n},{k})")
    print(f"Modo seleccionado: {modo.upper()}")
    print(f"Número de palabras: {num_palabras}")
    print(f"Ebf/N0 = {EbfN0_db} dB")
    print(f"Amplitud BPSK A = {A}")

    # ------------------------------------------------------------
    # FUENTE: genera U
    # ------------------------------------------------------------
    imprimir_bloque("FUENTE: genera U")

    U = generar_fuente(num_palabras, k)

    imprimir_matriz("U - palabras de fuente", U)

    # ------------------------------------------------------------
    # COD: U -> V
    # ------------------------------------------------------------
    imprimir_bloque("COD: entra U, sale V = U @ G mod 2")

    G = generar_matriz_generadora(k, n)

    V = codificar(U, G)

    imprimir_matriz("G - matriz generadora sistemática [I | P]", G)
    imprimir_matriz("V - palabras de código", V)

    # ------------------------------------------------------------
    # MATRIZ H Y VERIFICACIÓN
    # ------------------------------------------------------------
    imprimir_bloque("VERIFICACIÓN: V @ H.T mod 2 debe dar cero")

    H = generar_matriz_verificadora_de_paridad(G)

    S_verificacion = verificar_palabras_codigo(V, H)

    d_min = calcular_dmin(G, k)
    t_corrector = (d_min - 1) // 2
    t_detector = d_min - 1

    imprimir_matriz("H - matriz verificadora de paridad [P.T | I]", H)
    imprimir_matriz("S_verificacion = V @ H.T mod 2", S_verificacion)

    print(f"d_min = {d_min}")
    print(f"Errores que puede corregir: t = {t_corrector}")
    print(f"Errores que puede detectar: d_min - 1 = {t_detector}")

    # ------------------------------------------------------------
    # CANAL: V -> R
    # ------------------------------------------------------------
    imprimir_bloque("CANAL AWGN + BPSK: entra V, sale R")

    R, r_analogica, N0 = canal_awgn_bpsk(V, A, n, k, EbfN0_db)

    imprimir_matriz("R - bits recibidos luego de detección dura", R)

    print(f"N0 usado en el canal = {N0:.6f}")

    # ------------------------------------------------------------
    # DET/CORR: R -> V_e
    # ------------------------------------------------------------
    imprimir_bloque("DET/CORR: entra R, calcula S = R @ H.T mod 2, sale V_e")

    V_e, S, filas_aceptadas = detector_corrector(R, H, d_min, modo)

    imprimir_matriz("S - síndromes de las palabras recibidas", S)
    imprimir_matriz("V_e - palabras luego de detectar/corregir", V_e)

    if modo == "detector":
        print(f"Palabras aceptadas: {np.sum(filas_aceptadas)}")
        print(f"Palabras descartadas por síndrome no nulo: {np.sum(~filas_aceptadas)}")

    # ------------------------------------------------------------
    # DEC: V_e -> U_e
    # ------------------------------------------------------------
    imprimir_bloque("DEC: entra V_e, sale U_e")

    U_e = decodificar(V_e, k)

    imprimir_matriz("U_e - palabras de fuente estimadas", U_e)

    # ------------------------------------------------------------
    # RESULTADOS
    # ------------------------------------------------------------
    imprimir_bloque("RESULTADOS: comparación U vs U_e")

    metricas = calcular_metricas(U, U_e, filas_aceptadas, modo)

    print(f"Palabras comparadas: {metricas['palabras_comparadas']}")
    print(f"Palabras descartadas: {metricas['palabras_descartadas']}")
    print(f"Errores de palabra: {metricas['errores_palabra']}")
    print(f"Errores de bit: {metricas['errores_bit']}")
    print(f"P_ep estimada = {metricas['Pep']}")
    print(f"P_eb estimada = {metricas['Peb']}")

    if modo == "detector":
        print(f"P_descartadas = {metricas['P_descartadas']}")
        print(f"P_error_no_detectado_sobre_total = {metricas['P_error_no_detectado_sobre_total']}")

    # ------------------------------------------------------------
    # FLUJO COMPLETO
    # ------------------------------------------------------------
    imprimir_bloque("FLUJO COMPLETO")

    print("U -> COD -> V -> CANAL AWGN+BPSK -> R -> DET/CORR -> V_e -> DEC -> U_e")


if __name__ == "__main__":
    main()