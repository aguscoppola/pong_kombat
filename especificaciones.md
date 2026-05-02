# Pong Kombat - Documento de Especificaciones Técnicas

## Visión General del Proyecto
**Objetivo:** Implementar la **Versión 1.0 (MVP)** basada estrictamente en la arquitectura mecánica del Pong clásico. Las mecánicas experimentales ("Kombat") se planificarán en iteraciones posteriores (v2.0+). 

El proyecto está diseñado para ser implementado en Python, utilizando un Game Loop estandarizado y renderizado 2D (se sugiere la librería `pygame`). El código debe estar orientado a objetos (POO), desacoplando la lógica de físicas, renderizado y manejo de estado.

---

## Especificaciones de la Versión 1.0 (Core Engine)

### 1. Entidades del Juego (Game Objects)

*   **Paletas (Paddles):**
    *   **Geometría:** Rectángulos estáticos en el eje X, dinámicos en el eje Y.
    *   **Renderizado:** Color sólido (blanco puro `#FFFFFF`), sin sprites complejos en la v1.
    *   **Posicionamiento:** 
        *   Jugador 1 (Izquierda): Eje X fijado con un margen (offset) del borde izquierdo.
        *   Jugador 2 (Derecha): Eje X fijado con un margen simétrico del borde derecho.
    *   **Restricciones de Pantalla (Clamping):** Las coordenadas Y (`rect.top` y `rect.bottom`) deben estar delimitadas (`clamp`) por el alto de la ventana `SCREEN_HEIGHT` para evitar que las paletas salgan del área de juego utilizable.

*   **Pelota (Ball):**
    *   **Geometría:** Cuadrada (alto = ancho). Color blanco puro.
    *   **Cinemática:** Se desplaza actualizando su posición en función de un vector de velocidad en 2D `(Vx, Vy)`, preferiblemente normalizado y ajustado por el `delta_time` (independencia de framerate).
    *   **Aceleración (Escalamiento de Dificultad):** Tras cada colisión válida con una paleta, el módulo del vector velocidad aumentará por un factor constante (ej. `SPEED_MULTIPLIER = 1.05`) para evitar *loops* infinitos (partidas eternas).

### 2. Sistema de Controles (Input Handling)
El procesamiento de teclas debe evaluar el estado continuo del teclado por *frame* (tecla mantenida), evitando el *key repeat delay* nativo del sistema operativo.
*   **Jugador 1 (Izquierda):** Teclas `W` (Vector Y negativo / Subir) y `S` (Vector Y positivo / Bajar).
*   **Jugador 2 (Derecha):** Tecla `Flecha Arriba` (Vector Y negativo) y `Flecha Abajo` (Vector Y positivo).

### 3. Sistema de Físicas y Colisiones (AABB)
Todo el sistema de colisiones se basará en el teorema de intersección de rectángulos alineados a los ejes (Axis-Aligned Bounding Box).

*   **Colisiones con el Entorno (Limites Y):**
    *   **Techo y Suelo:** Si `ball.rect.top <= 0` o `ball.rect.bottom >= SCREEN_HEIGHT`, se invierte el componente Y del vector de velocidad de la pelota (`Vy = -Vy`).
*   **Anotación (Límites X):**
    *   Si la pelota supera `x <= 0`, se desencadena el evento `GOAL_PLAYER_2`.
    *   Si la pelota supera `x >= SCREEN_WIDTH`, se desencadena el evento `GOAL_PLAYER_1`.
*   **Colisión Entidad-Entidad (Pelota vs Paletas):**
    *   Al detectar intersección (`AABB collision`), se invierte el componente X del vector (`Vx = -Vx`).
    *   **Modificador de Ángulo:** El ángulo de rebote (vector `Vy`) se calculará dinámicamente según el punto de impacto. Si la pelota golpea el centro de la paleta, rebota horizontalmente. Si golpea los extremos, el ángulo de salida vertical se incrementa, ofreciendo control táctico a los jugadores.

### 4. Bucle Principal y Máquina de Estados (Game Loop & State)
El juego debe manejar al menos tres estados (`MENU`, `PLAYING`, `GAME_OVER`).

*   **Sistema de Puntuación:**
    *   Marcador renderizado en la parte superior central.
    *   UI: Línea punteada dividiendo el centro del campo (la "red").
*   **Reset de Punto (Servicio):**
    *   Tras un evento `GOAL`, la pelota se centra en `(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)`.
    *   Pausa de un (1) segundo antes de iniciar el movimiento.
    *   El vector inicial se dispara aleatoriamente hacia la dirección del jugador que acaba de recibir el punto en contra.
*   **Condición de Victoria (Win Condition):**
    *   Límite establecido por constante `MAX_SCORE = 12`.
    *   Al llegar a este umbral, el estado pasa a `GAME_OVER`, deteniendo las actualizaciones de físicas y mostrando el texto del ganador ("Player 1 Wins!" o "Player 2 Wins!"). Se habilita un *listener* para reiniciar la partida con una tecla (Ej: `SPACEBAR`).

---

## Roadmap v2.0+ 
### Mecánicas Nuevas: Modo Kombat (Poderes Especiales)

Se introducirá un sistema de poderes especiales para darle un giro dinámico y táctico al juego clásico.

**1. Sistema de Carga (Meter):**
* **Contador de Golpes:** Cada vez que un jugador golpea la pelota con su paleta, se suma 1 toque a su contador personal.
* **Reinicio de Contador:** Cada vez que un jugador anota un punto (hay un gol), los contadores de *ambos* jugadores se reinician automáticamente a 0.
* **Obtención de Poder:** Al acumular **7 toques** en una misma ronda, el jugador recibe un poder especial de forma aleatoria (suerte).

**2. Indicadores Visuales:**
Para que el jugador sepa qué poder le tocó, su paleta cambiará de color al llegar a los 7 toques:
*   **Paleta Roja:** Indica que obtuvo el Poder 1 (Bola Rápida).
*   **Paleta Verde:** Indica que obtuvo el Poder 2 (Paleta Gigante).

**3. Teclas de Activación:**
El jugador puede decidir en qué momento exacto usar su poder guardado presionando una tecla:
*   **Jugador 1:** Tecla `D`
*   **Jugador 2:** Tecla `Flecha Derecha`
**4. Lista de Poderes Especiales:**
*(Aparición al llegar a 7 toques: Rojo 30%, Verde 30%, Amarillo 30%, Naranja 10%)*
1.  **Bola Roja (Ofensivo):** Al activar este poder (paleta roja), el próximo impacto convertirá la pelota en color rojo y esta saldrá disparada al **doble de velocidad (x2)**. La pelota mantendrá esta súper-velocidad hasta que el oponente logre golpearla. Luego de usarlo, la paleta vuelve a ser blanca.
2.  **Escudo Gigante (Defensivo):** Al activar este poder (paleta verde), la paleta mutará y se volverá el **doble de grande (x2 de altura)**, haciendo muy fácil atajar la pelota. Esta ventaja durará exactamente **3 golpes**. Después del tercer golpe a la pelota, la paleta recuperará su tamaño normal y color blanco puro.
3.  **Velocista (Pasivo / Acumulable):** Al activar este poder (paleta amarilla), la velocidad de movimiento de la paleta aumentará un **50% extra**. Este poder es infinito hasta que se anote un gol. Además, ¡es acumulable! Si lo consigues dos veces seguidas sin que te anoten un gol, tendrás +100% de velocidad. **Mecánica de Reroll:** Si consigues este poder pero decides NO activarlo, al golpear la pelota 2 veces tu paleta mutará y se transformará en otro poder al azar.
4.  **Poder Naranja (Espejismo):** Sonido de caricatura ("uuui.wav"). La pelota se vuelve de color naranja, duplica su tamaño (x2) y **aumenta su velocidad un 50% extra (x1.5)**, volviéndose enorme, rápida y aterradora. A partir de ese momento, la pelota cruzará los bordes izquierdo y derecho como si fueran paredes, rebotando en lugar de ser gol y perdiendo el efecto al instante. Pero si un jugador la llega a tocar con su paleta, ¡esa paleta explota (sonido de "pop") y el rival anota un punto automáticamente! El poder se desactiva cuando alguien la toca o cuando rebota 1 vez en los bordes.

**5. Ítem de Campo: Reloj de Arena (Cámara Lenta, Maldición y Doble Filo)**
*   **Aparición Continua:** El primer reloj de arena aparece al llegar a **10 golpes globales**. A partir de ahí, **cada 5 toques adicionales** (golpes 15, 20, 25...), aparecerá un nuevo reloj en el centro, incluso si alguien ya había capturado uno antes o si ya había uno en pantalla.
*   **Probabilidades de Aparición:** Azul (25%), Amarillo (25%), Violeta (20%), Rojo (20%), Blanco (10%).

*   **Zona Azul (25% - Beneficio):** Suena una trompeta de victoria. La mitad de la pantalla de quien lo agarró se vuelve de color azul oscuro. Mientras la pelota viaje por esa zona, su velocidad se reducirá a la **mitad (0.5x)**. Esto le da a ese jugador muchísimo tiempo extra para predecir trayectorias, prepararse para atajar y usar sus poderes tácticos con total calma.
*   **Zona Roja (20% - Maldición):** Suena una alarma de error grave. La mitad de la pantalla de quien lo agarró se vuelve de color rojo oscuro. Mientras la pelota viaje por esa zona, su velocidad aumentará un **25%**. Esto funciona como una trampa, ya que el jugador tendrá mucho menos tiempo para reaccionar a los rebotes en su propia mitad.
*   **Reloj Violeta (Maldición):** 20% de probabilidad. "¡Ring!" misterioso (campana.wav). El fondo se vuelve violeta oscuro. Maldice a quien le dio el último golpe a la pelota. El jugador maldecido sufre amnesia y sus golpes acumulados vuelven a 0. Además, ahora solo necesitará 3 golpes para conseguir un poder (en lugar de 7), pero está obligado a usarlo apenas lo consiga o de lo contrario mutará súper rápido (cada 2 toques). El efecto dura hasta que se haga un gol.
*   **Reloj Blanco (Súper Paleta):** 10% de probabilidad. Sonido angelical divino (divino.wav). Quien lo captura obtiene una "Súper Paleta" blanca temporal. Tras un retraso de 0.05s, la paleta crece ocupando toda su mitad de la cancha. Mientras esté activa, la paleta te protege pero sus golpes no suman puntos para conseguir un power-up. Esta Súper Paleta dura exactamente 5 golpes (es decir, cada vez que la súper paleta rechaza la pelota). Al llegar al quinto rebote, la paleta vuelve instantáneamente a su tamaño normal, pierde cualquier poder que tuviera guardado y resetea sus toques a 0. Si el rival logra sobrevivir a los 5 embates y la paleta se rompe, ¡el rival es recompensado con un power-up aleatorio instantáneo! Además, mientras este reloj esté activo, no pueden aparecer nuevos relojes en la cancha.
*   **Reloj Amarillo (Crucifijo / Vida Extra):** 25% de probabilidad. Sonido mágico de vida (vida.wav). El jugador que logre golpear la pelota contra el reloj recibirá una Vida Extra. Esto se representa como una barrera gigante amarilla justo detrás de su paleta, en el límite de la pantalla. Si la pelota logra pasar su defensa, en lugar de ser un gol, chocará contra la barrera amarilla y rebotará de vuelta hacia la cancha, salvándole la vida. Al rebotar la pelota, la barrera se consume y desaparece instantáneamente. El efecto persiste aunque se agarre otro reloj, pero se reinicia si alguien marca un gol de manera normal. La captura implica que la pelota debe tocar el reloj para activarlo. El jugador que le haya pegado a la pelota antes del impacto será el dueño de la nueva zona (borrando la anterior).
*   **Reinicio:** La zona alterada (Azul, Roja, Violeta, Amarillo y Blanco) y el contador global de toques se reinician automáticamente cuando se anota un gol.