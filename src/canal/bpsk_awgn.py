import numpy as np


def canal_awgn_bpsk(
    V: np.ndarray,
    A: float,
    n: int,
    k: int,
    EbfN0_db: float
):
    """
    Canal AWGN + BPSK + detección dura.

        Es = A^2
        Ebf = Es*n/k
        s = (2*v - 1)*A
        N0 = Ebf/EbfN0
        noise = sqrt(N0/2)*(randn + j randn)
        r = s + noise
        vr = 1*(real(r)>0)
    """

    EbfN0_lineal = 10 ** (EbfN0_db / 10)

    Es = A ** 2
    Ebf = Es * (n / k)
    N0 = Ebf / EbfN0_lineal

    s = (2 * V.astype(float) - 1) * A

    ruido = np.sqrt(N0 / 2) * (
        np.random.randn(*V.shape) + 1j * np.random.randn(*V.shape)
    )

    r = s + ruido

    # Detección dura
    R = (r.real > 0).astype(np.uint8)

    return R, r, N0