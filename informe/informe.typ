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

El presente trabajo práctico tiene como objetivo modelar, simular y analizar un sistema de comunicación digital con codificación de canal y codificación de fuente. En la primera parte se estudia el desempeño de un sistema binario sobre un canal AWGN utilizando modulación BPSK y un código de bloque lineal sistemático $(14,10)$, con detección dura en recepción. El propósito de esta etapa es evaluar cómo la redundancia introducida por el código permite mejorar la confiabilidad de la transmisión, comparando el sistema codificado con el sistema sin codificación.

En particular, se analizan dos formas de utilización del código. En el primer caso, el código se emplea como corrector de errores, intentando recuperar la palabra transmitida a partir del síndrome de la palabra recibida. En el segundo caso, se utiliza como detector de errores, descartando las palabras cuyo síndrome indique que se produjo una alteración durante la transmisión. Para ambos modos se relevan curvas simuladas y teóricas de probabilidad de error de bit y de palabra en función de la relación $E_b/N_0$.

La segunda parte del trabajo consiste en aplicar codificación de fuente sobre una imagen binaria mediante el algoritmo de Huffman, considerando fuentes extendidas de orden 2 y 3. En este caso, el objetivo es aprovechar la redundancia estadística de la imagen para reducir el largo promedio de la secuencia codificada.

= Marco Teórico

== Sistema BPSK sobre canal AWGN

En un sistema binario antipodal, como BPSK, cada bit se transmite mediante un símbolo de amplitud positiva o negativa. En este trabajo se utilizó el siguiente mapeo:

$
  v = 0 arrow s = -A
$

$
  v = 1 arrow s = +A
$

Por lo tanto, para una palabra binaria $v$, la señal modulada puede escribirse como:

$
  s = (2v - 1)A
$

El canal considerado es AWGN, es decir, un canal con ruido blanco gaussiano aditivo. A nivel de símbolo, la señal recibida es:

$
  r = s + n
$



Luego, la detección dura se realiza observando el signo de la parte real de la señal recibida:

$
  v_r = cases(
    1 "si" Re(r) > 0,
    0 "si" Re(r) <= 0
  )
$

La probabilidad de error de bit de un sistema BPSK sobre AWGN está dada por:

$
  P_(e b) = Q(sqrt(2 E_b / N_0))
$ <eq-peb-bpsk>

donde $Q(x)$ es la función de cola de una variable normal estándar:

$
  Q(x) = 1/2 "erfc"(x / sqrt(2))
$

== Energía de bit de fuente y energía de bit de canal

En el sistema codificado no se transmiten directamente los bits de fuente, sino las palabras de código. Cada palabra de fuente de largo $k$ se transforma en una palabra de código de largo $n$. Por lo tanto, la tasa del código es:

$
  R_c = k/n
$

En este trabajo:

$
  R_c = 10/14 = 0.7143
$

Como se agregan bits de redundancia, la energía de bit de canal $E_(b c)$ no coincide con la energía de bit de fuente $E_(b f)$. Si la energía de símbolo BPSK es:

$
  E_s = A^2
$

y como en BPSK cada símbolo transporta un bit de canal:

$
  E_(b c) = E_s
$

La energía de bit de fuente resulta:

$
  E_(b f) = n/k E_(b c)
$

De esta relación se obtiene:

$
  E_(b c) = k/n E_(b f)
$

Por lo tanto, cuando se grafica en función de $E_(b f)/N_0$, la probabilidad de error del canal codificado debe calcularse como:

$
  p = Q(sqrt(2 k/n E_(b f)/N_0))
$ <eq-p-canal-codificado>

Esta penalidad energética explica por qué, a baja relación señal a ruido, el sistema codificado puede tener peor desempeño que el sistema sin codificación.

== Códigos de bloque lineales

Un código de bloque lineal $(n,k)$ toma bloques de $k$ bits de fuente y los transforma en bloques de $n$ bits de canal, con $n > k$. La codificación se realiza mediante una matriz generadora $G$:

$
  v = u G " mod " 2
$

donde $u$ es la palabra de fuente y $v$ es la palabra de código.

En un código sistemático, la matriz generadora se construye como:

$
  G = [I_k | P]
$

De esta manera, la palabra de código queda formada por los bits originales de fuente y los bits de paridad:

$
  v = [u | u P]
$

La matriz de control de paridad se construye como:

$
  H = [P^T | I_(n-k)]
$

y, en forma transpuesta:

$
  H^T = mat(
    P;
    I_(n-k)
  )
$

Estas matrices deben cumplir:

$
  G H^T " mod " 2 = 0
$

Esta condición garantiza que toda palabra de código válida tiene síndrome nulo.

== Síndrome

Luego de la transmisión por el canal y de la detección dura, se obtiene una palabra recibida $r$. Para verificar si esta palabra pertenece o no al código, se calcula el síndrome:

$
  s = r H^T " mod " 2
$ <eq-sindrome>

Para muchas palabras recibidas almacenadas en una matriz $R$, el cálculo se realiza en forma matricial:

$
  S = R H^T " mod " 2
$

Si $s = 0$, la palabra recibida pertenece al código y se acepta como válida. Si $s != 0$, se detecta que ocurrió al menos un error.

En modo corrector, el síndrome se utiliza para identificar la posición probable del bit erróneo. En modo detector, el síndrome solo se utiliza para decidir si la palabra se acepta o se descarta.

== Capacidad de corrección y detección

La distancia mínima de Hamming de un código, $d_"min"$, determina cuántos errores puede corregir o detectar sin ambigüedad. La cantidad máxima de errores corregibles es:

$
  t_c = floor((d_"min" - 1) / 2)
$ <eq-tc>

La cantidad máxima de errores detectables es:

$
  t_d = d_"min" - 1
$ <eq-td>

Para el código utilizado en este trabajo se obtuvo:

$
  d_"min" = 3
$

Por lo tanto:

$
  t_c = floor((3 - 1) / 2) = 1
$

$
  t_d = 3 - 1 = 2
$

Esto significa que el código puede corregir un error por palabra o detectar hasta dos errores por palabra, si se lo usa exclusivamente como detector.

== Probabilidad teórica de error en modo corrector

En modo corrector, el código corrige todos los patrones de error de peso menor o igual a $t_c$. Por lo tanto, se produce error de palabra cuando la cantidad de errores dentro de la palabra recibida supera la capacidad correctora del código.

La probabilidad teórica de error de palabra es:

$
  P_(e p,"corr") = sum_(i=t_c+1)^n binom(n, i) p^i (1-p)^(n-i)
$ <eq-pep-corrector-general>

Como en este trabajo $n=14$ y $t_c=1$, queda:

$
  P_(e p,"corr") = sum_(i=2)^14 binom(14, i) p^i (1-p)^(14-i)
$

equivalentemente:

$
  P_(e p,"corr") = 1 - (1-p)^14 - 14p(1-p)^13
$

Para valores altos de $E_(b f)/N_0$, se cumple $p << 1$, por lo que domina el término de dos errores:

$
  P_(e p,"corr") approx binom(14, 2)p^2
$

La probabilidad de error de bit de fuente puede aproximarse, para $p << 1$, como:

$
  P_(e b,"corr") approx ((2t_c + 1) / n) binom(n, t_c + 1) p^(t_c + 1)
$

En este caso:

$
  P_(e b,"corr") approx (3/14) binom(14, 2)p^2
$

== Probabilidad teórica en modo detector

En modo detector, una palabra se descarta cuando su síndrome es no nulo:

$
  s = r H^T != 0
$

Por otro lado, un error no detectado ocurre cuando el patrón de error $e$ produce síndrome nulo:

$
  e H^T = 0
$

Esto sucede cuando el patrón de error coincide con una palabra de código no nula. Por lo tanto, la probabilidad de error no detectado puede calcularse sumando sobre todas las palabras de código no nulas:

$
  P_"und" = sum_(c in C, c != 0) p^(w_H (c)) (1-p)^(n - w_H (c))
$ <eq-pund>

donde $w_H (c)$ es el peso de Hamming de la palabra de código $c$.

La probabilidad de aceptación total es:

$
  P_"acept" = sum_(c in C) p^(w_H (c)) (1-p)^(n - w_H (c))
$

y la probabilidad de descarte es:

$
  P_"desc" = 1 - P_"acept"
$

Como el código tiene $d_"min" = 3$, las palabras de código no nulas de menor peso tienen peso 3. Por eso, para alta relación señal a ruido, la probabilidad de error no detectado queda dominada por los errores de peso 3:

$
  P_"und" approx A_3 p^3
$

donde $A_3$ es la cantidad de palabras de código de peso 3. Para el código utilizado se obtuvo $A_3 = 28$, por lo que:

$
  P_"und" approx 28 p^3
$

== Ganancia asintótica

La ganancia de codificación permite medir cuánta reducción de $E_b/N_0$ se logra para obtener una misma probabilidad de error. En este trabajo, como se utiliza detección dura, corresponde usar la expresión de ganancia asintótica para decisión dura:

$
  G_a = k/n floor((d_"min" + 1) / 2)
$ <eq-ganancia-asintotica>

Reemplazando los valores del código:

$
  G_a = 10/14 floor((3 + 1) / 2)
$

$
  G_a = 10/14 dot 2 = 1.4286
$

En decibeles:

$
  G_a ["dB"] = 10 log_10 (1.4286)
$

$
  G_a ["dB"] = 1.5490 " dB"
$

Este valor representa la ganancia esperada en el régimen asintótico, es decir, para probabilidades de error muy bajas o valores altos de $E_(b f)/N_0$.

= Codificación de Canal

== Definición del sistema simulado

Para estructurar la simulación, se modeló el enlace de comunicaciones mediante bloques funcionales secuenciales. El flujo implementado fue:

$
  U -> V -> R -> V_e -> U_e
$

donde:

+ $U$: matriz de palabras de fuente. Cada fila contiene una palabra binaria de longitud $k=10$.
+ $V$: matriz de palabras de código obtenida mediante $V = U G " mod " 2$.
+ $R$: matriz de palabras recibidas luego de la modulación BPSK, transmisión por canal AWGN y detección dura.
+ $V_e$: matriz de palabras corregidas o aceptadas, según el modo de operación.
+ $U_e$: matriz de palabras de fuente estimadas luego de la decodificación.

#figure(
  image("../src/resultados/figuras/diagrama.png", width: 90%),
  caption: [Diagrama en bloques del sistema de comunicación digital simulado.],
) <fig-diagrama-sistema>

La fuente genera bits binarios equiprobables e independientes. Estos bits se agrupan en filas de largo $k=10$, formando la matriz $U$. Luego, el codificador de canal aplica la matriz generadora $G$ para obtener las palabras codificadas de largo $n=14$.

El canal equivalente incluye la modulación BPSK, la suma de ruido blanco gaussiano aditivo y la detección dura. Finalmente, el receptor calcula el síndrome de cada palabra recibida y actúa de manera diferente según el modo de operación: en modo corrector intenta corregir el error, mientras que en modo detector descarta las palabras con síndrome no nulo.

== Definición del código y matrices

Para implementar el código de bloque lineal $(14,10)$ sistemático, se propuso la siguiente matriz de paridad $P$ de tamaño $10 times 4$:

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

A partir de esta matriz se construyó la matriz generadora sistemática:

$
  G = [I_10 | P]
$

y la matriz de control de paridad:

$
  H = [P^T | I_4]
$

Para verificar que las matrices fueran compatibles, se comprobó por código que:

$
  G H^T " mod " 2 = 0
$

Esto confirma que todas las palabras generadas por $G$ pertenecen al espacio nulo de $H$, es decir, son palabras válidas del código.

== Parámetros del código

Al evaluar todas las palabras de código posibles, se obtuvo una distancia mínima:

$
  d_"min" = 3
$

Por lo tanto, el código puede corregir un error por palabra o detectar hasta dos errores por palabra.

#table(
  columns: 2,
  [Parámetro], [Valor],
  [Longitud de palabra de código $n$], [14],
  [Longitud de palabra de fuente $k$], [10],
  [Redundancia $n-k$], [4],
  [Tasa del código $R_c = k/n$], [0.7143],
  [Distancia mínima $d_"min"$], [3],
  [Capacidad correctora $t_c$], [1 error],
  [Capacidad detectora $t_d$], [2 errores],
  [Ganancia asintótica dura], [1.5490 dB],
) <tab-parametros-codigo>

== Implementación de la simulación

Para cada valor de $E_(b f)/N_0$, se generaron $100.000$ palabras de fuente de $10$ bits. Luego se codificaron mediante:

$
  V = U G " mod " 2
$

La transmisión se realizó usando BPSK sobre AWGN. La amplitud de los símbolos fue elegida respetando la relación entre energía de bit de fuente y energía de bit de canal:

$
  E_(b c) = k/n E_(b f)
$

Por lo tanto, al normalizar $E_(b f)=1$, la amplitud BPSK queda:

$
  A = sqrt(k/n)
$

La palabra modulada se obtuvo como:

$
  s = (2V - 1)A
$

Luego se sumó ruido gaussiano de varianza asociada al $N_0$ correspondiente:

$
  N_0 = E_(b f) / (E_(b f)/N_0)
$

Finalmente, se aplicó detección dura:

$
  R = 1(Re(r) > 0)
$

A partir de $R$, el receptor calculó los síndromes:

$
  S = R H^T " mod " 2
$

y procedió según el modo de operación.

== Modo corrector

En modo corrector, si el síndrome de una palabra recibida es nulo, la palabra se considera válida. Si el síndrome es no nulo y coincide con una fila de $H^T$, se interpreta como un error simple y se invierte el bit correspondiente.

Como el código tiene $d_"min"=3$, solo puede corregir un error por palabra. Si ocurren dos o más errores en una misma palabra, el decodificador puede equivocarse, ya que el síndrome resultante puede coincidir con el de otro error simple. En ese caso, el receptor invierte un bit incorrecto y puede aumentar la cantidad de errores en la palabra final.

#figure(
  image("../src/resultados/figuras/canal_corrector.png", width: 85%),
  caption: [Curvas de probabilidad de error de bit y de palabra para el código $(14,10)$ en modo corrector.],
) <fig-canal-corrector>

En la @fig-canal-corrector se observa que, para valores bajos de $E_(b f)/N_0$, la curva simulada de error de bit con código se encuentra por encima de la curva sin codificación. Esto significa que, en esa región, el código empeora el desempeño del sistema.

Este comportamiento se debe principalmente a dos motivos. Primero, al agregar redundancia, se transmiten $14$ bits de canal por cada $10$ bits de fuente. Si se mantiene fija la energía por bit de fuente, cada bit de canal se transmite con menor energía:

$
  E_(b c) = k/n E_(b f)
$

Por lo tanto, el canal introduce más errores sobre los bits codificados. Segundo, a baja relación señal a ruido es frecuente que ocurran dos o más errores dentro de una misma palabra. Como el código solo puede corregir un error, el decodificador puede tomar una decisión incorrecta.

A medida que aumenta $E_(b f)/N_0$, la probabilidad de error del canal disminuye. En esa región, los errores simples son mucho más probables que los errores múltiples, y el código logra corregirlos correctamente. Por eso, a partir de aproximadamente $4.5$ dB, la curva de error de bit codificada comienza a quedar por debajo de la curva sin codificación.

Esto muestra la ganancia de codificación: para una misma probabilidad de error, el sistema codificado requiere una menor relación $E_(b f)/N_0$ que el sistema sin codificación. En alta relación señal a ruido, la pendiente de la curva codificada mejora porque el error queda dominado por eventos de dos o más errores, cuya probabilidad es proporcional a $p^2$.

#figure(
  caption: [Resultados de la simulación en modo corrector para distintas relaciones señal a ruido.],
  table(
    columns: 4,
    [$E_(b f)/N_0$ dB], [$P_(e b)$ simulada], [$P_(e p)$ simulada], [Palabras corregidas],
    [0.0], [0.121122], [0.49561], [76869],
    [2.0], [0.053921], [0.23600], [59585],
    [4.0], [0.013111], [0.06057], [33257],
    [5.0], [0.004734], [0.02213], [21036],
    [6.0], [0.001286], [0.00610], [11286],
    [7.0], [0.000254], [0.00131], [5109],
    [8.0], [0.000034], [0.00016], [1894],
    [9.0], [0.000005], [0.00002], [504],
  ),
) <tab-resultados-corrector>

La @tab-resultados-corrector confirma numéricamente lo observado en el gráfico. A medida que aumenta $E_(b f)/N_0$, disminuyen tanto la probabilidad de error de bit como la probabilidad de error de palabra. También se reduce la cantidad de palabras corregidas, porque el canal produce cada vez menos errores.

Es importante notar que en $10$ dB no se observaron errores en la simulación. Esto no significa que la probabilidad real sea exactamente cero, sino que con $100.000$ palabras transmitidas no ocurrió ningún evento de error. Para estimar probabilidades más bajas sería necesario simular una cantidad mayor de palabras.

== Modo detector

En modo detector, el receptor no intenta corregir la palabra recibida. Solamente calcula el síndrome:

$
  s = r H^T " mod " 2
$

Si el síndrome es nulo, la palabra se acepta. Si el síndrome es no nulo, la palabra se descarta. Por lo tanto, el modo detector prioriza la confiabilidad de las palabras aceptadas, pero puede perder una gran cantidad de información cuando el canal es ruidoso.

#figure(
  image("../src/resultados/figuras/canal_detector.png", width: 85%),
  caption: [Desempeño del código $(14,10)$ en modo detector. Se muestran la probabilidad de descarte y las probabilidades de error asociadas a las palabras aceptadas.],
) <fig-canal-detector>

En la @fig-canal-detector se observa que, para bajos valores de $E_(b f)/N_0$, la probabilidad de descarte es muy alta. Por ejemplo, a $0$ dB se descarta aproximadamente el $80%$ de las palabras transmitidas. Esto ocurre porque el ruido del canal altera con frecuencia al menos un bit de la palabra, generando un síndrome no nulo.

A medida que aumenta $E_(b f)/N_0$, la probabilidad de error del canal disminuye, y por lo tanto también disminuye la cantidad de palabras descartadas. Por ejemplo, a $5$ dB se descarta aproximadamente el $21%$ de las palabras, mientras que a $10$ dB solo se descarta aproximadamente el $0.1%$.

La probabilidad de error no detectado es mucho menor que la probabilidad de descarte. Esto se debe a que un error no detectado solo ocurre si el patrón de error transforma la palabra transmitida en otra palabra válida del código. En términos del síndrome, esto significa:

$
  e H^T = 0
$

Como el código tiene $d_"min"=3$, los errores no detectados más probables son de peso 3. Por eso, para valores altos de $E_(b f)/N_0$, su probabilidad cae proporcionalmente a $p^3$, mucho más rápido que la probabilidad de error simple.

#figure(
  caption: [Desempeño numérico del código operando en modo detector.],
  table(
    columns: 5,
    [$E_(b f)/N_0$ dB], [$P_"desc"$], [$P_"und,total"$], [$P_(e p)$ en aceptadas], [Palabras aceptadas],
    [0.0], [0.80453], [0.01605], [0.08211], [19547],
    [2.0], [0.61075], [0.00484], [0.01243], [38925],
    [3.0], [0.47949], [0.00174], [0.00334], [52051],
    [4.0], [0.33795], [0.00054], [0.00082], [66205],
    [5.0], [0.21125], [0.00010], [0.00013], [78875],
    [6.0], [0.11257], [0.00000], [0.00000], [88743],
    [8.0], [0.01893], [0.00000], [0.00000], [98107],
    [10.0], [0.00115], [0.00000], [0.00000], [99885],
  ),
) <tab-resultados-detector>

En la @tab-resultados-detector se distinguen dos métricas diferentes. La columna $P_"und,total"$ representa la cantidad de palabras erróneas aceptadas sobre el total de palabras transmitidas. En cambio, $P_(e p)$ en aceptadas representa la tasa de error de palabra considerando únicamente las palabras que no fueron descartadas.

A partir de $6$ dB no se observaron errores no detectados en la simulación. Esto no significa que la probabilidad teórica sea exactamente cero, sino que la cantidad de eventos esperados es muy baja para el tamaño de simulación utilizado. Para medir con mayor precisión esa región sería necesario transmitir una cantidad mucho mayor de palabras.

== Comparación entre modo corrector y modo detector

El modo corrector y el modo detector tienen objetivos distintos.

En modo corrector, el receptor intenta recuperar todas las palabras transmitidas. Esto permite mantener la continuidad de la información, pero tiene el riesgo de corregir incorrectamente cuando ocurren errores múltiples. Por eso, a baja relación señal a ruido, el código puede empeorar el desempeño respecto del sistema sin codificación.

En modo detector, el receptor no intenta recuperar las palabras alteradas, sino que las descarta. Esto reduce fuertemente la probabilidad de aceptar datos erróneos, pero a costa de perder palabras. Este modo sería adecuado en un sistema con retransmisión, donde las palabras descartadas puedan volver a enviarse. Sin retransmisión, la información descartada se pierde.

Desde el punto de vista de la confiabilidad, el modo detector entrega palabras aceptadas más seguras. Desde el punto de vista de la continuidad de la información, el modo corrector resulta más conveniente, especialmente cuando la relación $E_(b f)/N_0$ es suficientemente alta.

== Análisis desde la ganancia de código

La ganancia de código se observa comparando la curva codificada con la curva sin codificación para una misma probabilidad de error. En el gráfico del modo corrector, a bajas relaciones $E_(b f)/N_0$, el sistema codificado se comporta peor que el sistema sin codificación debido a la penalidad energética y a los errores múltiples.

Sin embargo, a partir de la zona de cruce, aproximadamente alrededor de $4.5$ dB, la curva codificada comienza a quedar por debajo de la curva sin codificación. Esto indica que el código empieza a aportar una mejora real en la transmisión.

En el régimen de alta relación señal a ruido, la probabilidad de error del sistema codificado disminuye más rápidamente que la del sistema sin codificación. Esto se debe a que, en el sistema sin codificación, un único error de canal produce un error de bit, mientras que en el sistema codificado corrector se necesitan al menos dos errores dentro de la misma palabra para que falle la decodificación.

La ganancia asintótica calculada para este código con decisión dura fue:

$
  G_a = 1.5490 " dB"
$

Este valor representa la mejora esperada cuando $E_(b f)/N_0$ tiende a valores altos. En la simulación, la tendencia de las curvas es coherente con este resultado: el código no siempre mejora el desempeño, pero sí lo hace en la región de baja probabilidad de error.

= Conclusiones de la codificación de canal

Se implementó y simuló un sistema de comunicación digital BPSK sobre canal AWGN utilizando un código de bloque lineal sistemático $(14,10)$ con detección dura. A partir de la matriz de paridad propuesta, se construyeron las matrices $G$ y $H$, verificando que $G H^T " mod " 2 = 0$. Además, se obtuvo una distancia mínima $d_"min"=3$, lo cual permite corregir un error por palabra o detectar hasta dos errores.

En modo corrector, el código mejora el desempeño del sistema solo a partir de cierto valor de $E_(b f)/N_0$. Para valores bajos, la redundancia reduce la energía por bit de canal y aumenta la probabilidad de errores múltiples, lo que puede perjudicar la decodificación. Para valores altos de $E_(b f)/N_0$, los errores simples predominan y el código logra corregirlos, reduciendo tanto la probabilidad de error de bit como la de palabra.

En modo detector, el sistema descarta todas las palabras con síndrome no nulo. Esto reduce fuertemente la probabilidad de aceptar palabras erróneas, pero puede provocar una gran pérdida de información cuando el canal es ruidoso. Por este motivo, el modo detector resulta especialmente útil en sistemas donde sea posible solicitar retransmisiones.

Finalmente, la ganancia asintótica calculada fue de $1.5490$ dB para decisión dura. Las curvas simuladas muestran un comportamiento coherente con este resultado, ya que la mejora del sistema codificado se vuelve visible en la región de alta relación señal a ruido.
