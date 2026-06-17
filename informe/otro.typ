#import "@preview/barcala:0.3.0": apendice, informe, nomenclatura
#import "@preview/lilaq:0.5.0" as lq
#import "@preview/physica:0.9.7": *
#import "@preview/zero:0.5.0"

#show: informe.with(
  unidad-academica: "ingeniería",
  asignatura: "E1603 Teoría de la Información y Codificación",
  trabajo: "TRABAJO PRÁCTICO DE SIMULACIÓN",

  autores: (
    (
      nombre: "Avila Montoya, Eygleen Fernanda",
      email: "eygleen.avila@alu.ing.unlp.edu.ar",
      legajo: "02931/2",
    ),
  ),

  titulo: [Simulación de un Sistema de Comunicación Digital: Codificación de Fuente y Canal],

  resumen: [*_Objetivo_ --- Simular y evaluar el desempeño de un sistema de comunicación digital sobre un canal AWGN. En primer lugar, se implementa un código de bloque lineal (14,10) con modulación BPSK, analizando las tasas de error en modos de corrección y detección para determinar la ganancia de codificación. En segundo lugar, se aplica el algoritmo de Huffman para la compresión sin pérdidas de una imagen TIFF utilizando fuentes extendidas, evaluando el largo promedio y la tasa de compresión resultante.*],

  fecha: "2026-06-17",
)

// Enlaces de colores
#show cite: set text(blue)
#show link: set text(blue)
#show ref: set text(blue)

// Bloques de matemática con números para citar
#set math.equation(numbering: "(1)")
#show ref: it => {
  if it.element != none and it.element.func() == math.equation {
    link(it.element.location(), numbering(
      it.element.numbering,
      ..counter(math.equation).at(it.element.location()),
    ))
  } else {
    it
  }
}

// Configuración de `zero` (Opcional, útil para tablas de resultados)
#import zero: num, zi
#zero.set-num(decimal-separator: ",")



= Introducción
El presente trabajo práctico tiene como propósito principal modelar y analizar los extremos de un sistema de comunicación digital. Por un lado, se busca proteger la integridad de los datos frente a las perturbaciones del medio físico mediante la implementación de un código de bloque lineal (14,10). Por otro lado, se explora la eliminación de redundancia intrínseca en los datos a través de la codificación de fuente empleando el algoritmo de Huffman sobre un archivo de imagen.

= Marco Teórico
Para evaluar el desempeño del sistema codificado, es necesario compararlo con las cotas teóricas. En un sistema binario antipodal como BPSK operando sobre un canal AWGN, la probabilidad de error de bit sin codificar está dada por:

$
  P_(e b) = Q(sqrt(2 E_b / N_0))
$ <eq-peb-bpsk>

Al introducir un código de bloque lineal $(n, k)$ capaz de corregir hasta $t_c$ errores, la probabilidad de error de palabra bajo decisión dura se aproxima mediante la distribución binomial:

$
  P_(e p) approx sum_(i=t_c+1)^n binom(n, i) p^i (1-p)^(n-i)
$ <eq-pep-codificada>

donde $p$ es la probabilidad de error en el canal (con su respectiva penalidad por redundancia). Para valores altos de relación señal a ruido, la mejora del sistema se cuantifica mediante la ganancia asintótica $G_a$.


= Resultados y Discusión

== Codificación de Canal: Modo Corrector
// AQUI: Pegar el gráfico de src/resultados/figuras/canal_corrector.png
// Analizar la ganancia de código observando el cruce de las curvas.





== Codificación de Canal: Modo Detector
// AQUI: Pegar el gráfico de src/resultados/figuras/canal_detector.png
// Analizar la diferencia entre P_ep y la altísima tasa de palabras descartadas.




== Codificación de Fuente: Algoritmo de Huffman
// AQUI: Insertar la tabla de resultados (largo promedio y tasa de compresión) generada en CSV.

= Conclusiones
// Responder a las preguntas del PDF:
// 1. A partir de qué valor de Eb/N0 conviene usar el corrector.
// 2. Justificar por qué Huffman comprime la imagen a pesar de que los píxeles blancos y negros sean equiprobables.
