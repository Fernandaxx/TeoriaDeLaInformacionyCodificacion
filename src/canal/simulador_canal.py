import numpy as np

from canal.codificador import generar_fuente, codificar, decodificar_sistematico
from canal.bpsk_awgn import canal_awgn_bpsk
from canal.sindromes import detector_corrector
from canal.metricas_canal import calcular_metricas
from canal.matrices import (
    generar_matriz_generadora,
    generar_matriz_verificadora_de_paridad,
    calcular_dmin,
)


def simular_un_punto(
    EbfN0_db: float,
    num_palabras: int,
    k: int,
    n: int,
    A: float,
    modo: str,
    G=None,
    H=None,
    d_min=None,
) -> dict:
    """
    Ejecuta el flujo completo para un valor de Ebf/N0.

    U -> V -> R -> Ve -> Ue
    """
    if G is None:
        G = generar_matriz_generadora(k, n)

    if H is None:
        H = generar_matriz_verificadora_de_paridad(G)

    if d_min is None:
        d_min = calcular_dmin(G)

    U = generar_fuente(num_palabras, k)

    V = codificar(U, G)

    R, _, _ = canal_awgn_bpsk(
        V=V,
        A=A,
        n=n,
        k=k,
        EbfN0_db=EbfN0_db
    )

    V_e, _, filas_aceptadas, estadisticas = detector_corrector(
        R=R,
        H=H,
        d_min=d_min,
        modo=modo
    )

    U_e = decodificar_sistematico(V_e, k)

    metricas = calcular_metricas(U, U_e, filas_aceptadas)

    metricas["EbfN0_db"] = float(EbfN0_db)
    metricas.update(estadisticas)

    return metricas


def simular_curva(
    EbfN0_db_vector,
    num_palabras: int,
    k: int,
    n: int,
    A: float,
    modo: str,
) -> list:

    G = generar_matriz_generadora(k, n)
    H = generar_matriz_verificadora_de_paridad(G)
    d_min = calcular_dmin(G)

    resultados = []

    print()
    print("=" * 100)
    print(f"SIMULACIÓN CANAL - MODO {modo.upper()}")
    print("=" * 100)
    print(f"{'Eb/N0 [dB]':<12} | {'Peb':<14} | {'Pep':<14} | {'Descartadas':<14}")
    print("-" * 100)

    for EbfN0_db in EbfN0_db_vector:
        metricas = simular_un_punto(
            EbfN0_db=EbfN0_db,
            num_palabras=num_palabras,
            k=k,
            n=n,
            A=A,
            modo=modo,
            G=G,
            H=H,
            d_min=d_min,
        )

        resultados.append(metricas)

        print(
            f"{EbfN0_db:<12.1f} | "
            f"{metricas['Peb']:<14.6e} | "
            f"{metricas['Pep']:<14.6e} | "
            f"{metricas['P_descartadas']:<14.6e}"
        )

    return resultados