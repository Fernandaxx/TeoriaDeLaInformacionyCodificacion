import numpy as np
import matplotlib.pyplot as plt

from canal.teorico_canal import (
    peb_teorica_sin_codigo,
    pep_teorica_corrector,
    prob_detector_teorica,
)


def _array_resultados(resultados: list, clave: str):
    return np.array([r[clave] for r in resultados], dtype=float)


def graficar_resultados_canal(
    resultados: list,
    k: int,
    n: int,
    d_min: int,
    modo: str,
    ruta_salida=None,
    G=None,
):

    EbfN0_db_vector = _array_resultados(resultados, "EbfN0_db")
    Peb_sim = reemplazar_ceros_por_nan(_array_resultados(resultados, "Peb"))
    Pep_sim = reemplazar_ceros_por_nan(_array_resultados(resultados, "Pep"))
    P_descartadas = reemplazar_ceros_por_nan(_array_resultados(resultados, "P_descartadas"))

    Peb_sin_codigo_teo = np.array([
        peb_teorica_sin_codigo(x) for x in EbfN0_db_vector
    ])

    plt.figure(figsize=(10, 6))

    plt.semilogy(
        EbfN0_db_vector,
        Peb_sin_codigo_teo,
        "k-",
        label="P_eb sin código teórica"
    )

    plt.semilogy(
        EbfN0_db_vector,
        Peb_sim,
        "bo-",
        label=f"P_eb simulada con código ({modo})"
    )

    plt.semilogy(
        EbfN0_db_vector,
        Pep_sim,
        "rs-",
        label=f"P_ep simulada con código ({modo})"
    )

    if modo == "corrector":
        t = (d_min - 1) // 2

        Pep_teo = np.array([
            pep_teorica_corrector(x, n, k, t) for x in EbfN0_db_vector
        ])

        plt.semilogy(
            EbfN0_db_vector,
            Pep_teo,
            "r--",
            label="P_ep teórica corrector"
        )

    if modo == "detector":
        plt.semilogy(
            EbfN0_db_vector,
            P_descartadas,
            "g^-",
            label="P descartadas simulada"
        )

        if G is not None:
            P_desc_teo = np.array([
                prob_detector_teorica(x, G, k, n)["P_descartadas_teo"]
                for x in EbfN0_db_vector
            ])

            P_no_det_teo = np.array([
                prob_detector_teorica(x, G, k, n)["P_error_no_detectado_teo"]
                for x in EbfN0_db_vector
            ])

            plt.semilogy(
                EbfN0_db_vector,
                P_desc_teo,
                "g--",
                label="P descartadas teórica"
            )

            plt.semilogy(
                EbfN0_db_vector,
                P_no_det_teo,
                "m--",
                label="P error no detectado teórica"
            )

    plt.xlabel("Ebf/N0 [dB]")
    plt.ylabel("Probabilidad")
    plt.title(f"Curvas de error - Código ({n},{k}) - Modo {modo}")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()

    if ruta_salida is not None:
        plt.savefig(ruta_salida, dpi=300)

    plt.show()
    
def reemplazar_ceros_por_nan(y):
    y = np.array(y, dtype=float)
    y[y == 0] = np.nan
    return y