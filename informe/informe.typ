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
  fecha: "2026-06-17",
)

#show cite: set text(blue)
#show link: set text(blue)
#show ref: set text(blue)
#set math.equation(numbering: "(1)")
#set text(lang: "es")

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

#import zero: num, zi
#zero.set-num(decimal-separator: ",")

= Introducción

El presente trabajo práctico tiene como objetivo modelar, simular y analizar el desempeño de  de un sistema de comunicación digital.\
En la primera etapa se estudia la transmisión sobre un canal con Ruido Blanco Gaussiano Aditivo (AWGN) empleando modulación BPSK. Se implementa un código de bloque lineal sistemático $(14,10)$ con detección dura. El desempeño se evalúa operando el código tanto en modo corrector como en modo detector, relevando las curvas de probabilidad de error en función de la relación $E_b/N_0$ y comparándolas con las cotas analíticas teóricas.\
En la segunda etapa, se explora la compresión de datos sin pérdidas aplicando el algoritmo de codificación de fuente de Huffman sobre una imagen binaria. Se implementan fuentes extendidas de orden 2 y 3 para aprovechar la redundancia espacial de la imagen, calculando las tasas de compresión logradas. Finalmente, se simula la transmisión del archivo comprimido a través del canal ruidoso codificado para recuperar la imagen original, validando el funcionamiento conjunto del sistema.

= Fundamentos teóricos

== Sistema BPSK sobre canal AWGN

En un sistema BPSK antipodal, cada bit de canal se representa mediante una amplitud positiva o negativa. En la simulación se utilizó el mapeo:

$
  v = 0 arrow s = -A
$

$
  v = 1 arrow s = +A
$

Por lo tanto, para una palabra binaria $v$, la señal modulada queda expresada como:

$
  s = (2v - 1) A
$ <eq-bpsk>

El canal considerado es AWGN. A nivel de símbolo, la muestra recibida se modela como:

$
  r = s + n
$



Luego de la recepción, se aplica detección dura sobre la parte real de la muestra recibida:

$
  v_r = cases(
    1 "si" Re(r) > 0,
    0 "si" Re(r) <= 0
  )
$

Para BPSK sin codificación, la probabilidad de error de bit está dada por:

$
  P_(e b) = Q(sqrt(2 E_b / N_0))
$ <eq-peb-bpsk>

con:

$
  Q(x) = 1/2 "erfc"(x / sqrt(2))
$

== Energía de bit de fuente y energía de bit de canal

En el sistema codificado, cada bloque de $k$ bits de fuente se transforma en una palabra de código de $n$ bits. La tasa del código es:

$
  R_c = k/n = 10/14 = 0.7143
$

Como BPSK transmite un bit de canal por símbolo, se cumple:

$
  E_(b c) = E_s = A^2
$

La energía de bit de fuente resulta:

$
  E_(b f) = n/k E_(b c)
$

Por lo tanto:

$
  E_(b c) = k/n E_(b f)
$ <eq-ebc-ebf>

Esta relación es importante porque las curvas se grafican en función de $E_(b f)/N_0$. Si se normaliza $E_(b f)=1$, la amplitud BPSK empleada en el sistema codificado queda:

$
  A = sqrt(k/n)
$

La probabilidad de transición equivalente luego de la detección dura se calcula entonces como:

$
  p = Q(sqrt(2 k/n E_(b f)/N_0))
$ <eq-p-canal-codificado>

== Código de bloque lineal sistemático

Un código de bloque lineal $(n,k)$ transforma una palabra de fuente $u$ de $k$ bits en una palabra de código $v$ de $n$ bits mediante una matriz generadora $G$:

$
  v = u G " mod " 2
$

Para una implementación sistemática, la matriz generadora se construye como:

$
  G = [I_k | P]
$

De esta manera, la palabra de código queda formada por los bits originales de fuente y los bits de paridad:

$
  v = [u | u P]
$

La matriz de control de paridad asociada se construye como:

$
  H = [P^T | I_(n-k)]
$



La condición de compatibilidad entre ambas matrices es:

$
  G H^T " mod " 2 = 0
$ <eq-gh>

Esta igualdad garantiza que toda palabra generada por $G$ tenga síndrome nulo.

== Síndrome, corrección y detección

Luego de la detección dura se obtiene una palabra recibida $r$. El síndrome se calcula como:

$
  s = r H^T " mod " 2
$ <eq-sindrome>

Para una matriz $R$ de palabras recibidas, el cálculo se realiza vectorialmente:

$
  S = R H^T " mod " 2
$

En modo corrector, si el síndrome es no nulo y coincide con una fila de $H^T$, se interpreta como un error simple y se invierte el bit correspondiente. En modo detector, no se corrige la palabra recibida: si el síndrome es no nulo, la palabra se descarta.

La distancia mínima de Hamming del código determina cuántos errores pueden corregirse o detectarse sin ambigüedad:

$
  t_c = floor((d_"min" - 1) / 2)
$ <eq-tc>

$
  t_d = d_"min" - 1
$ <eq-td>

Para el código implementado se obtuvo $d_"min" = 3$. Por lo tanto:

$
  t_c = 1
$

$
  t_d = 2
$

El código puede corregir un error por palabra o detectar hasta dos errores por palabra cuando se utiliza únicamente como detector.

== Probabilidades teóricas de error

En modo corrector, la palabra se decodifica correctamente si ocurren como máximo $t_c$ errores en los $n$ bits de canal. Por lo tanto, la probabilidad teórica de error de palabra es:

$
  P_(e p,"corr") = sum_(i=t_c+1)^n binom(n, i) p^i (1-p)^(n-i)
$ <eq-pep-corrector>

Como $n=14$ y $t_c=1$:

$
  P_(e p,"corr") = sum_(i=2)^14 binom(14, i) p^i (1-p)^(14-i)
$

Para alta relación señal a ruido, $p << 1$, domina el término de dos errores:

$
  P_(e p,"corr") approx binom(14, 2) p^2
$

La probabilidad de error de bit de fuente se aproxima, en el mismo régimen, por:

$
  P_(e b,"corr") approx ((2t_c + 1) / n) binom(n, t_c + 1) p^(t_c + 1)
$ <eq-peb-corrector>

En modo detector, una palabra errónea no detectada ocurre cuando el patrón de error tiene síndrome nulo. Esto sucede si el patrón de error coincide con una palabra de código no nula. Por lo tanto:

$
  P_"und" = sum_(c in C, c != 0) p^(w_H(c)) (1-p)^(n - w_H(c))
$ <eq-pund>

La probabilidad de aceptación total es:

$
  P_"acept" = sum_(c in C) p^(w_H(c)) (1-p)^(n - w_H(c))
$

y la probabilidad de descarte resulta:

$
  P_"desc" = 1 - P_"acept"
$ <eq-pdesc>

Como $d_"min"=3$, los errores no detectados más probables son de peso 3. En el código empleado se obtuvo $A_3 = 28$, por lo que en alta relación señal a ruido:

$
  P_"und" approx 28 p^3
$

== Ganancia asintótica

La ganancia de código se interpreta como la reducción necesaria de $E_b/N_0$ para alcanzar una misma probabilidad de error. En el régimen asintótico, para decisión dura, se empleó:

$
  G_a = k/n floor((d_"min" + 1) / 2)
$ <eq-ga>

Reemplazando $k=10$, $n=14$ y $d_"min"=3$:

$
  G_a = 10/14 dot 2 = 1.4286
$

En decibeles:

$
  G_a ["dB"] = 10 log_10(1.4286) = 1.5490 " dB"
$

Este valor corresponde a la mejora esperada cuando $E_(b f)/N_0$ tiende a valores altos.

= Codificación de canal

== Matrices propuestas y verificación

Para implementar el código de bloque lineal sistemático $(14,10)$, se propuso la siguiente matriz de paridad $P$ de tamaño $10 times 4$:

$
  P = mat(
    0, 0, 1, 1;
    0, 1, 0, 1;
    0, 1, 1, 0;
    0, 1, 1, 1;
    1, 0, 0, 1;
    1, 0, 1, 0;
    1, 0, 1, 1;
    1, 1, 0, 0;
    1, 1, 0, 1;
    1, 1, 1, 0
  )
$

Con esta matriz se definieron:

$
  G = [I_10 | P]
$

$
  H = [P^T | I_4]
$

Por construcción, el código es sistemático: las primeras $k=10$ posiciones de cada palabra codificada corresponden a los bits de fuente. La verificación $G H^T " mod " 2 = 0$ fue realizada por programa, confirmándose que todas las palabras generadas pertenecen al código.

#figure(
  table(
    columns: 2,
    align: left,
    [Parámetro], [Valor],
    [Longitud de palabra de código $n$], [14],
    [Longitud de palabra de fuente $k$], [10],
    [Redundancia $n-k$], [4],
    [Tasa del código $R_c=k/n$], [0.7143],
    [Distancia mínima $d_"min"$], [3],
    [Capacidad correctora $t_c$], [1 error],
    [Capacidad detectora $t_d$], [2 errores],
    [Ganancia asintótica con decisión dura], [1.5490 dB],
  ),
  caption: [Parámetros del código de bloque lineal implementado.],
) <tab-parametros-codigo>

== Metodología de simulación

Para cada valor de $E_(b f)/N_0$ se generaron $10^7$ palabras de fuente de longitud $k=10$. La matriz de fuente $U$ fue codificada en forma matricial mediante:

$
  V = U G " mod " 2
$

El canal equivalente incluyó modulación BPSK, ruido AWGN complejo y decisión dura. La secuencia recibida fue obtenida mediante:

$
  R = 1(Re(r) > 0)
$

A partir de $R$ se calcularon los síndromes:

$
  S = R H^T " mod " 2
$\
Finalmente, en modo corrector se aplicó la tabla de síndromes para invertir el bit asociado a errores simples. En modo detector se descartaron las palabras con síndrome no nulo. Como la codificación es sistemática, la decodificación consistió en extraer las primeras $k$ columnas de la matriz corregida o aceptada.\
Las métricas se calcularon comparando la matriz de bits de fuente estimados $U_e$ con la matriz original $U$. En modo detector, antes de la comparación se eliminaron de $U$ las filas correspondientes a palabras descartadas. Por este motivo, $P_(e b)$ se interpreta como tasa de error de bit de fuente, mientras que $P_(e p)$ se interpreta como tasa de error de palabra de fuente luego de la decodificación.

== Resultados en modo corrector

#figure(
  image("../src/resultados/figuras/canal_corrector.png", width: 85%),
  caption: [Curvas de probabilidad de error para el código $(14,10)$ utilizado como corrector.],
) <fig-canal-corrector>

En la @fig-canal-corrector se comparan las curvas simuladas con las curvas teóricas. Para valores bajos de $E_(b f)/N_0$, la probabilidad de error de bit del sistema codificado queda por encima de la curva sin codificación. Este comportamiento se justifica por la penalidad energética introducida por la redundancia: al mantener fija la energía por bit de fuente, cada bit de canal se transmite con energía $E_(b c)=k/n E_(b f)$.\
Además, en baja relación señal a ruido aumenta la probabilidad de que ocurran dos o más errores dentro de una misma palabra. Como el código solo corrige un error, el decodificador puede invertir un bit incorrecto y generar una palabra final errónea.\
A partir de aproximadamente $4.5$ dB, la curva codificada comienza a ubicarse por debajo de la curva sin codificación. En esta región, los errores simples son dominantes y el código logra corregirlos. En alta relación señal a ruido, el error queda dominado por eventos de peso 2 o mayor, por lo que la pendiente de la curva codificada mejora respecto de la curva sin codificación.

#figure(
  table(
    columns: 4,
    align: center,
    [$E_(b f)/N_0$ dB], [$P_(e b)$ sim.], [$P_(e p)$ sim.], [Palabras corregidas],
    [0.0], [0.120994], [0.495076], [7 691 360],
    [0.5], [0.102981], [0.429556], [7 361 007],
    [1.0], [0.085417], [0.362951], [6 959 128],
    [1.5], [0.068810], [0.297503], [6 484 144],
    [2.0], [0.053758], [0.236243], [5 941 856],
    [2.5], [0.040461], [0.180299], [5 331 656],
    [3.0], [0.029263], [0.132188], [4 685 990],
    [3.5], [0.020160], [0.092168], [4 008 254],
    [4.0], [0.013235], [0.061104], [3 335 716],
    [4.5], [0.008179], [0.038085], [2 686 921],
    [5.0], [0.004774], [0.022406], [2 089 918],
    [5.5], [0.002586], [0.012224], [1 567 551],
    [6.0], [0.001306], [0.006205], [1 126 469],
    [6.5], [0.000606], [0.002888], [774 966],
    [7.0], [0.000255], [0.001214], [506 402],
    [7.5], [0.000102], [0.000484], [316 530],
    [8.0], [3.30e-05], [0.000159], [185 914],
    [8.5], [9.47e-06], [4.48e-05], [102 447],
    [9.0], [2.75e-06], [1.29e-05], [52 750],
    [9.5], [4.80e-07], [2.60e-06], [25 052],
    [10.0], [8.00e-08], [5.00e-07], [10 999],
  ),
  caption: [Resultados simulados en modo corrector. Cada punto fue estimado con $10^7$ palabras de fuente.],
) <tab-resultados-corrector>

La @tab-resultados-corrector muestra la disminución progresiva de $P_(e b)$ y $P_(e p)$ al aumentar $E_(b f)/N_0$. También se observa que la cantidad de palabras corregidas disminuye con la relación señal a ruido, ya que se producen menos errores simples en el canal. A $10$ dB se obtuvieron 5 palabras erróneas sobre $10 000 000$ palabras transmitidas, lo que confirma que la simulación alcanza la zona de muy baja probabilidad de error, aunque una estimación todavía más precisa requeriría más palabras transmitidas.

== Resultados en modo detector

#figure(
  image("../src/resultados/figuras/canal_detector.png", width: 85%),
  caption: [Curvas de desempeño para el código $(14,10)$ utilizado como detector.],
) <fig-canal-detector>

En modo detector, el receptor no intenta corregir las palabras alteradas. Solamente se acepta una palabra cuando su síndrome es nulo. Por ese motivo, para valores bajos de $E_(b f)/N_0$ se descarta una fracción elevada de palabras transmitidas. A $0$ dB, la probabilidad de descarte fue aproximadamente $0.8057$, mientras que a $10$ dB disminuyó a aproximadamente $0.0011$.\
La probabilidad de error no detectado fue mucho menor que la probabilidad de descarte. Esto se debe a que no alcanza con que ocurra un error: para que el error no sea detectado, el patrón de error debe transformar la palabra transmitida en otra palabra válida del código. Dado que $d_"min"=3$, los errores no detectados más probables son de peso 3, por lo que su probabilidad decrece más rápidamente que la probabilidad de error simple.

#figure(
  table(
    columns: 5,
    align: center,
    [$E_(b f)/N_0$ dB], [$P_"desc"$], [$P_"und,total"$], [$P_(e p)$ aceptadas], [Palabras aceptadas],
    [0.0], [0.805705], [0.016263], [0.083703], [1 942 955],
    [0.5], [0.768099], [0.012640], [0.054508], [2 319 008],
    [1.0], [0.723302], [0.009549], [0.034512], [2 766 975],
    [1.5], [0.671090], [0.006841], [0.020800], [3 289 105],
    [2.0], [0.611722], [0.004646], [0.011967], [3 882 778],
    [2.5], [0.547254], [0.002977], [0.006576], [4 527 455],
    [3.0], [0.478587], [0.001827], [0.003504], [5 214 125],
    [3.5], [0.408078], [0.001029], [0.001739], [5 919 224],
    [4.0], [0.337980], [0.000542], [0.000819], [6 620 197],
    [4.5], [0.271412], [0.000264], [0.000363], [7 285 876],
    [5.0], [0.210620], [0.000115], [0.000146], [7 893 801],
    [5.5], [0.157605], [4.13e-05], [4.90e-05], [8 423 947],
    [6.0], [0.113323], [1.77e-05], [2.00e-05], [8 866 772],
    [6.5], [0.077984], [6.10e-06], [6.62e-06], [9 220 159],
    [7.0], [0.050935], [1.30e-06], [1.37e-06], [9 490 653],
    [7.5], [0.031568], [3.00e-07], [3.10e-07], [9 684 321],
    [8.0], [0.018607], [1.00e-07], [1.02e-07], [9 813 927],
    [8.5], [0.010245], [0.000000], [0.000000], [9 897 549],
    [9.0], [0.005259], [0.000000], [0.000000], [9 947 407],
    [9.5], [0.002510], [0.000000], [0.000000], [9 974 898],
    [10.0], [0.001109], [0.000000], [0.000000], [9 988 910],
  ),
  caption: [Resultados simulados en modo detector. $P_"und,total"$ se calculó sobre el total transmitido y $P_(e p)$ aceptadas sobre las palabras no descartadas.],
) <tab-resultados-detector>

En la @tab-resultados-detector se distinguen dos formas de medir el error en modo detector. La columna $P_"und,total"$ mide la cantidad de palabras erróneas aceptadas respecto del total de palabras transmitidas. En cambio, $P_(e p)$ aceptadas mide la tasa de error condicionada a las palabras que no fueron descartadas. A partir de $8.5$ dB no se observaron errores no detectados en la simulación. Esto no implica que la probabilidad teórica sea nula, sino que los eventos esperados son muy poco frecuentes para el tamaño de muestra utilizado.

== Comparación entre corrector y detector

El modo corrector y el modo detector presentan compromisos distintos. En modo corrector se intenta recuperar todas las palabras transmitidas, por lo que no se pierde información por descarte. Sin embargo, si ocurren errores múltiples, el decodificador puede corregir de manera incorrecta.\
En modo detector se prioriza la confiabilidad de las palabras aceptadas. Las palabras con síndrome no nulo se eliminan, reduciendo la probabilidad de entregar información errónea, pero a costa de perder datos. Este modo sería adecuado si el sistema contara con retransmisión. Sin retransmisión, las palabras descartadas representan pérdida de información útil.\
Desde el punto de vista de ganancia de código, el comportamiento relevante se observa en modo corrector. En baja relación señal a ruido, el código no mejora el desempeño debido a la penalidad energética y a los errores múltiples. En cambio, a partir de la zona de cruce, cercana a $4.5$ dB, la curva codificada presenta menor tasa de error que la curva sin codificación. En alta relación señal a ruido, la tendencia es coherente con la ganancia asintótica calculada de $1.5490$ dB.

= Codificación de fuente

== Metodología

La imagen `logo FI.tif` fue leída y convertida a una matriz binaria. Se asignó un valor binario a cada píxel:

$
  "negro" -> 0, quad "blanco" -> 1
$

Luego, la matriz fue convertida en un vector unidimensional de bits. A partir de este vector se formaron bloques de longitud $q$, donde $q=2$ para la fuente extendida de orden 2 y $q=3$ para la fuente extendida de orden 3. Cada bloque fue convertido a su representación decimal para facilitar el conteo de frecuencias.

Las probabilidades fueron estimadas mediante frecuencia relativa:

$
  p_i = f_i / N_s
$

donde $f_i$ es la frecuencia del símbolo $i$ y $N_s$ es la cantidad total de símbolos extendidos. Con esas probabilidades se construyó el árbol de Huffman y se obtuvo la regla de codificación.

Para evaluar la compresión se calcularon:

$
  overline(L)_"bloque" = sum_i p_i l_i
$

$
  overline(L)_"bit" = overline(L)_"bloque" / q
$

$
  H_"bloque" = - sum_i p_i log_2(p_i)
$

$
  H_"bit" = H_"bloque" / q
$

$
  T_c = L_"original" / L_"codificada"
$ <eq-tasa-compresion>

El código de Huffman es un código de prefijo. Por lo tanto, la decodificación puede realizarse de manera unívoca, siempre que la secuencia comprimida sea recibida sin errores residuales.

== Fuente extendida de orden 2

Para la fuente extendida de orden 2, la imagen de tamaño $434 times 432$ píxeles generó $187 488$ bits originales. Al agrupar los bits de a dos, se obtuvieron $93 744$ símbolos extendidos.

#figure(
  table(
    columns: 6,
    align: center,
    [Símbolo], [Bloque], [Frecuencia], [Probabilidad], [Código Huffman], [Longitud],
    [0], [00], [44 527], [0.474985], [01], [2],
    [1], [01], [860], [0.009174], [000], [3],
    [2], [10], [1 090], [0.011627], [001], [3],
    [3], [11], [47 267], [0.504214], [1], [1],
  ),
  caption: [Código Huffman obtenido para fuente extendida de orden 2.],
) <tab-huffman-orden2>

En la @tab-huffman-orden2 se observa que los bloques `00` y `11` concentran la mayor parte de la probabilidad. Por este motivo, Huffman asigna códigos más cortos a los bloques homogéneos y códigos más largos a los bloques de transición `01` y `10`.

#figure(
  table(
    columns: 2,
    align: left,
    [Métrica], [Valor],
    [Bits originales], [187 488],
    [Símbolos extendidos], [93 744],
    [Bits codificados], [142 171],
    [Largo promedio por bloque], [1.516588],
    [Largo promedio por bit de fuente], [0.758294],
    [Entropía por bloque], [1.145078],
    [Entropía por bit], [0.572539],
    [Tasa de compresión], [1.318750],
  ),
  caption: [Métricas de compresión para fuente extendida de orden 2.],
) <tab-metricas-orden2>

La tasa de compresión obtenida fue:

$
  T_c = 187488 / 142171 = 1.318750
$

Esto indica que la secuencia codificada ocupa aproximadamente el $75.83$ % de la longitud original.

== Fuente extendida de orden 3

Para la fuente extendida de orden 3, los $187 488$ bits originales se agruparon en bloques de tres bits, obteniéndose $62 496$ símbolos extendidos.

#figure(
  table(
    columns: 6,
    align: center,
    [Símbolo], [Bloque], [Frecuencia], [Probabilidad], [Código Huffman], [Longitud],
    [0], [000], [29 087], [0.465422], [11], [2],
    [1], [001], [567], [0.009073], [10001], [5],
    [2], [010], [10], [0.000160], [100001], [6],
    [3], [011], [774], [0.012385], [1011], [4],
    [4], [100], [594], [0.009505], [1001], [4],
    [5], [101], [1], [1.60e-05], [100000], [6],
    [6], [110], [626], [0.010017], [1010], [4],
    [7], [111], [30 837], [0.493424], [0], [1],
  ),
  caption: [Código Huffman obtenido para fuente extendida de orden 3.],
) <tab-huffman-orden3>

En la @tab-huffman-orden3 se observa nuevamente que los bloques homogéneos son los más probables. El bloque `111` recibió una palabra de un bit, mientras que `000` recibió una palabra de dos bits. Los bloques menos frecuentes recibieron longitudes mayores.

#figure(
  table(
    columns: 2,
    align: left,
    [Métrica], [Valor],
    [Bits originales], [187 488],
    [Símbolos extendidos], [62 496],
    [Bits codificados], [99 888],
    [Largo promedio por bloque], [1.598310],
    [Largo promedio por bit de fuente], [0.532770],
    [Entropía por bloque], [1.289044],
    [Entropía por bit], [0.429681],
    [Tasa de compresión], [1.876982],
  ),
  caption: [Métricas de compresión para fuente extendida de orden 3.],
) <tab-metricas-orden3>

La tasa de compresión obtenida fue:

$
  T_c = 187488 / 99888 = 1.876982
$

En este caso, la secuencia codificada ocupa aproximadamente el $53.28$ % de la longitud original.

== Comparación entre orden 2 y orden 3

#figure(
  table(
    columns: 7,
    align: center,
    [Orden],
    [Bits originales],
    [Bits codificados],
    [$overline(L)_"bloque"$],
    [$overline(L)_"bit"$],
    [$H_"bit"$],
    [Compresión],

    [2], [187 488], [142 171], [1.516588], [0.758294], [0.572539], [1.318750],
    [3], [187 488], [99 888], [1.598310], [0.532770], [0.429681], [1.876982],
  ),
  caption: [Comparación global entre la codificación Huffman de orden 2 y orden 3.],
) <tab-comparacion-huffman>

La @tab-comparacion-huffman muestra que el largo promedio por bloque es mayor para orden 3 que para orden 2. Sin embargo, esta comparación directa no es la más representativa, porque cada símbolo de orden 3 contiene tres bits originales, mientras que cada símbolo de orden 2 contiene dos bits. Por lo tanto, debe compararse el largo promedio por bit de fuente.

Para orden 2 se obtuvo:

$
  overline(L)_("bit, orden 2") = 0.758294
$

Para orden 3 se obtuvo:

$
  overline(L)_("bit, orden 3") = 0.532770
$

Por lo tanto, la fuente extendida de orden 3 logró mayor compresión. La mejora se debe a que, al agrupar más bits, se aprovechan mejor las correlaciones entre píxeles vecinos.

== Justificación de la compresión con píxeles casi equiprobables

Aunque los píxeles blancos y negros de la imagen sean casi equiprobables, eso no implica que los bits consecutivos sean independientes. A partir de las frecuencias de orden 2 puede estimarse:

$
  P(0) approx 0.4854
$

$
  P(1) approx 0.5146
$

Si los píxeles se analizaran individualmente, la fuente binaria sería cercana a equiprobable y la compresión sería limitada. Sin embargo, al analizar bloques se observa una distribución muy desigual. Para orden 2:

$
  P(00) + P(11) approx 0.9792
$

mientras que:

$
  P(01) + P(10) approx 0.0208
$

Para orden 3 ocurre algo similar:

$
  P(000) + P(111) approx 0.9588
$

Como la imagen tiene regiones continuas de blanco y negro, son mucho más frecuentes las secuencias homogéneas que las transiciones. Huffman aprovecha esta desigualdad asignando palabras más cortas a los bloques más probables, lo que permite comprimir aunque las probabilidades marginales de blanco y negro sean cercanas a $0.5$.

== Opcional 2: transmisión del mensaje comprimido

Se simuló la transmisión del mensaje comprimido mediante el sistema de canal desarrollado en la primera parte. El flujo utilizado fue:

$
  "imagen" -> "Huffman" -> "canal codificado" -> "Huffman inverso" -> "imagen recuperada"
$

Primero se comprimió la imagen mediante Huffman. Luego, la secuencia binaria comprimida se transmitió utilizando el código lineal $(14,10)$ con BPSK sobre AWGN y decodificación por síndrome. Finalmente, la secuencia recuperada fue decodificada con Huffman inverso para reconstruir la imagen.

#figure(
  grid(
    columns: 2,
    gutter: 1em,
    image("../src/resultados/figuras/comparacion_orden2_EbN0_7.0dB.png", width: 100%),
    image("../src/resultados/figuras/comparacion_orden2_EbN0_10.0dB.png", width: 100%),

    image("../src/resultados/figuras/comparacion_orden3_EbN0_7.0dB.png", width: 100%),
    image("../src/resultados/figuras/comparacion_orden3_EbN0_10.0dB.png", width: 100%),
  ),
  caption: [Comparación visual entre la imagen original y la imagen recuperada para Huffman de orden 2 y 3, transmitida a $E_b/N_0=7$ dB y $10$ dB.],
) <fig-comparacion-huffman>

La reconstrucción de la imagen depende fuertemente de la calidad del canal. Para $E_b/N_0 = 7$ dB se observan errores visibles, causados por errores residuales luego de la decodificación de canal. Como Huffman es un código de longitud variable, un error residual puede afectar la sincronización de la decodificación y propagarse a varios símbolos posteriores.\
Para $E_b/N_0 = 10$ dB, la imagen recuperada resulta visualmente similar a la original. Esto es coherente con la menor probabilidad de error del canal en esa región. El orden 3 logra mayor compresión, pero también puede resultar más sensible a errores residuales, porque una alteración en la secuencia comprimida puede afectar la interpretación de palabras de longitud variable.

= Conclusiones

Se implementó y evaluó un sistema de comunicación digital con codificación de canal y codificación de fuente. En la parte de canal se propuso un código de bloque lineal sistemático $(14,10)$ con $d_"min"=3$, capaz de corregir un error por palabra o detectar hasta dos errores si se lo utiliza exclusivamente como detector.
\
En modo corrector, se comprobó que el código no mejora el desempeño para bajas relaciones $E_(b f)/N_0$ debido a la penalidad energética y a la presencia de errores múltiples. Sin embargo, a partir de aproximadamente $4.5$ dB, la curva codificada supera al sistema sin codificación. En alta relación señal a ruido, la tendencia simulada es coherente con la ganancia asintótica de $1.5490$ dB calculada para decisión dura.
\
En modo detector, se verificó que la probabilidad de aceptar palabras erróneas es muy baja, especialmente en alta relación señal a ruido. No obstante, esta mejora en confiabilidad se obtiene a costa de descartar palabras recibidas con síndrome no nulo. Por este motivo, el modo detector resulta más adecuado para sistemas con retransmisión.
En la parte de fuente, la codificación Huffman permitió comprimir la imagen binaria. Para orden 2 se obtuvo una tasa de compresión de $1.318750$ y un largo promedio de $0.758294$ bits por bit de fuente. Para orden 3 se obtuvo una tasa de compresión de $1.876982$ y un largo promedio de $0.532770$ bits por bit de fuente. La mejora con orden 3 se explica por la mayor capacidad de la fuente extendida para aprovechar las correlaciones de la imagen.
\
Finalmente, mediante el opcional 2 se verificó que la transmisión de la secuencia comprimida requiere una baja tasa de error residual. La compresión de fuente elimina redundancia estadística, pero también vuelve a la secuencia más sensible a errores de canal. Por lo tanto, en un sistema completo debe considerarse el compromiso entre eficiencia de compresión, protección frente al ruido y fidelidad de reconstrucción.
