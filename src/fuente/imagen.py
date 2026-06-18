import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def cargar_imagen_binaria(ruta_imagen: str, umbral: int = 127):

    imagen = Image.open(ruta_imagen).convert("L")
    matriz_gris = np.array(imagen, dtype=np.uint8)

    matriz_binaria = (matriz_gris > umbral).astype(np.uint8)
    bits = matriz_binaria.reshape(-1)

    return matriz_binaria, bits


def guardar_imagen_binaria(bits: np.ndarray, shape_original, ruta_salida: str):
 
    matriz = bits.reshape(shape_original)
    imagen_uint8 = (matriz * 255).astype(np.uint8)

    Image.fromarray(imagen_uint8).save(ruta_salida)

    return imagen_uint8


def guardar_comparacion_imagenes(
    imagen_original,
    imagen_recuperada,
    ruta_salida: str,
    titulo: str
):


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
    plt.savefig(ruta_salida, dpi=300)
    plt.show()