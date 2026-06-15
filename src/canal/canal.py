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

from scipy.special import erfc
import matplotlib.pyplot as plt


# ============================================================
# ANÁLISIS TEÓRICO
# ============================================================

def Q(x):
    """
    Función Q usando erfc.
    """
    return 0.5 * erfc(x / np.sqrt(2))


def peb_teorica_sin_codigo(EbfN0_db):
    """
    Probabilidad teórica de error de bit para BPSK sin codificación.
    """
    EbfN0 = 10 ** (EbfN0_db / 10)
    return Q(np.sqrt(2 * EbfN0))


def p_error_canal_codificado(EbfN0_db, k, n):
    """
    Probabilidad de error de bit en el canal para el sistema codificado.

    Ojo:
    El eje está en Ebf/N0, energía de bit de fuente.
    Pero cada bit transmitido por el canal tiene energía menor porque agregamos redundancia.

    R = k/n
    Ebc/N0 = R * Ebf/N0
    """
    R = k / n
    EbfN0 = 10 ** (EbfN0_db / 10)

    return Q(np.sqrt(2 * R * EbfN0))


def pep_teorica_corrector(EbfN0_db, n, k, t):
    """
    Probabilidad teórica aproximada de error de palabra para código corrector.

    Si corrige hasta t errores, falla cuando aparecen t+1 o más errores.
    """
    from math import comb

    p = p_error_canal_codificado(EbfN0_db, k, n)

    Pep = 0.0

    for i in range(t + 1, n + 1):
        Pep += comb(n, i) * (p ** i) * ((1 - p) ** (n - i))

    return Pep


# ============================================================
# SIMULACIÓN PARA UN Eb/N0
# ============================================================

def simular_un_punto(EbfN0_db, num_palabras, k, n, A, modo):
    """
    Ejecuta TODO el flujo para un único valor de Ebf/N0.

    U -> COD -> V -> CANAL -> R -> DET/CORR -> V_e -> DEC -> U_e
    """

    # ------------------------------------------------------------
    # FUENTE: genera U
    # ------------------------------------------------------------
    U = generar_fuente(num_palabras, k)

    # ------------------------------------------------------------
    # COD: U -> V
    # ------------------------------------------------------------
    G = generar_matriz_generadora(k, n)
    V = codificar(U, G)

    # ------------------------------------------------------------
    # H y d_min
    # ------------------------------------------------------------
    H = generar_matriz_verificadora_de_paridad(G)
    d_min = calcular_dmin(G, k)

    # ------------------------------------------------------------
    # CANAL: V -> R
    # ------------------------------------------------------------
    R, r_analogica, N0 = canal_awgn_bpsk(V, A, n, k, EbfN0_db)

    # ------------------------------------------------------------
    # DET/CORR: R -> V_e
    # ------------------------------------------------------------
    V_e, S, filas_aceptadas = detector_corrector(R, H, d_min, modo)

    # ------------------------------------------------------------
    # DEC: V_e -> U_e
    # ------------------------------------------------------------
    U_e = decodificar(V_e, k)

    # ------------------------------------------------------------
    # MÉTRICAS
    # ------------------------------------------------------------
    metricas = calcular_metricas(U, U_e, filas_aceptadas, modo)

    return metricas


# ============================================================
# SIMULACIÓN DE CURVA COMPLETA
# ============================================================

def simular_curva(EbfN0_db_vector, num_palabras, k, n, A, modo):
    """
    Repite la simulación para varios valores de Ebf/N0.
    Guarda P_eb y P_ep simuladas.
    """

    Peb_sim = []
    Pep_sim = []
    P_descartadas = []

    print("\n" + "=" * 100)
    print(f"SIMULACIÓN COMPLETA - MODO {modo.upper()}")
    print("=" * 100)

    print(f"{'Ebf/N0 [dB]':<12} | {'P_eb sim':<15} | {'P_ep sim':<15} | {'Descartadas':<15}")
    print("-" * 100)

    for EbfN0_db in EbfN0_db_vector:

        metricas = simular_un_punto(
            EbfN0_db=EbfN0_db,
            num_palabras=num_palabras,
            k=k,
            n=n,
            A=A,
            modo=modo
        )

        Peb_sim.append(metricas["Peb"])
        Pep_sim.append(metricas["Pep"])
        P_descartadas.append(metricas["P_descartadas"])

        print(
            f"{EbfN0_db:<12.1f} | "
            f"{metricas['Peb']:<15.6e} | "
            f"{metricas['Pep']:<15.6e} | "
            f"{metricas['P_descartadas']:<15.6e}"
        )

    return np.array(Peb_sim), np.array(Pep_sim), np.array(P_descartadas)


# ============================================================
# GRÁFICOS
# ============================================================

def graficar_resultados(EbfN0_db_vector, Peb_sim, Pep_sim, k, n, d_min, modo):
    """
    Grafica las curvas simuladas y algunas teóricas.
    """

    t = (d_min - 1) // 2

    Peb_sin_codigo_teo = np.array([
        peb_teorica_sin_codigo(x) for x in EbfN0_db_vector
    ])

    Pep_teo_corr = np.array([
        pep_teorica_corrector(x, n, k, t) for x in EbfN0_db_vector
    ])

    plt.figure(figsize=(10, 6))

    plt.semilogy(EbfN0_db_vector, Peb_sin_codigo_teo, "k-", label="P_eb sin código teórica")
    plt.semilogy(EbfN0_db_vector, Peb_sim, "bo-", label=f"P_eb simulada con código ({modo})")
    plt.semilogy(EbfN0_db_vector, Pep_sim, "rs-", label=f"P_ep simulada con código ({modo})")

    if modo == "corrector":
        plt.semilogy(EbfN0_db_vector, Pep_teo_corr, "r--", label="P_ep teórica corrector")

    plt.xlabel("Ebf/N0 [dB]")
    plt.ylabel("Probabilidad de error")
    plt.title(f"Curvas de error - Código ({n},{k}) - Modo {modo}")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.show()

# ============================================================
# MAIN
# ============================================================

def main():

    np.random.seed(7)

    # ============================================================
    # CONFIGURACIÓN GENERAL
    # ============================================================

    k = 10
    n = 14
    A = 1.0

    #modo = "corrector"
    modo = "detector"

    num_palabras = 100_000

    EbfN0_db_vector = np.arange(0, 10.5, 0.5)

    print("\n" + "=" * 100)
    print("CONFIGURACIÓN DEL SISTEMA")
    print("=" * 100)

    print(f"Código: ({n},{k})")
    print(f"Modo: {modo.upper()}")
    print(f"Cantidad de palabras por punto: {num_palabras}")
    print(f"Valores de Ebf/N0: {EbfN0_db_vector}")

    # ============================================================
    # MATRICES DEL CÓDIGO
    # ============================================================

    G = generar_matriz_generadora(k, n)
    H = generar_matriz_verificadora_de_paridad(G)

    d_min = calcular_dmin(G, k)
    t_corrector = (d_min - 1) // 2
    t_detector = d_min - 1

    print("\n" + "=" * 100)
    print("PARÁMETROS DEL CÓDIGO")
    print("=" * 100)

    print(f"d_min = {d_min}")
    print(f"Puede corregir hasta {t_corrector} error/es por palabra")
    print(f"Puede detectar hasta {t_detector} error/es por palabra")

    # ============================================================
    # SIMULACIÓN
    # ============================================================

    Peb_sim, Pep_sim, P_descartadas = simular_curva(
        EbfN0_db_vector=EbfN0_db_vector,
        num_palabras=num_palabras,
        k=k,
        n=n,
        A=A,
        modo=modo
    )

    # ============================================================
    # GRÁFICOS
    # ============================================================

    graficar_resultados(
        EbfN0_db_vector=EbfN0_db_vector,
        Peb_sim=Peb_sim,
        Pep_sim=Pep_sim,
        k=k,
        n=n,
        d_min=d_min,
        modo=modo
    )


if __name__ == "__main__":
    main()