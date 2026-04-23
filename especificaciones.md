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
# Mecánicas Nuevas (Kombat)
*(Por definir. Espacio reservado para especificaciones futuras de power-ups, físicas no lineales, barras de salud o mecánicas de combate).*
