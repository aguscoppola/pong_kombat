# Pong Kombat - Documento de Especificaciones Técnicas (v0.3.1)

## 1. Visión General
**Pong Kombat** es una evolución del clásico arcade que introduce mecánicas de combate, gestión de poderes y alteración del entorno mediante ítems. El juego está construido sobre un motor de físicas AABB personalizado en Python con `pygame`.

---

## 2. Sistema de Controles (Input Mapping)
El manejo de entradas es continuo (sin retraso de repetición del SO).

### Jugador 1 (Izquierda)
*   **W / S**: Movimiento Vertical (Subir / Bajar).
*   **D**: Activar Poder Especial guardado.

### Jugador 2 (Derecha)
*   **Flecha Arriba / Abajo**: Movimiento Vertical.
*   **Flecha Derecha**: Activar Poder Especial guardado.

### Controles Globales
*   **ENTER**: Iniciar juego desde el menú / Reiniciar tras Game Over.
*   **ESCAPE**: Volver al menú principal desde una partida activa.
*   **MOUSE**: Navegación por el panel de modificadores, pestañas y acordeones.

---

## 3. Mecánicas del Core Engine

### Físicas de Rebote (Ángulo Dinámico)
El ángulo de salida de la pelota no es un simple reflejo. Se calcula según el punto de impacto en la paleta:
*   **Fórmula:** `ángulo = (distancia_al_centro / (altura_paleta / 2)) * MAX_BOUNCE_ANGLE`
*   **Resultado:** Golpear con los extremos de la paleta da ángulos más cerrados; golpear con el centro dispara la pelota de forma más horizontal.

### Aceleración Progresiva
*   La velocidad de la pelota aumenta tras cada impacto con una paleta.
*   El factor de aumento es configurable mediante el modificador **"Ball speed increase per hit"**.

---

## 4. Panel de Modificadores (Detalle Meticuloso)

### Pestaña "ALL" (Configuración Global)
1.  **Score Limit:** Define la puntuación necesaria para ganar (`5, 7, 10, 12, 15, 20`).
2.  **Ball Speed Increase:** Multiplicador de aceleración por impacto (`1.01` a `1.10`).
3.  **MATCH POINT:** Si está activo, requiere ganar por **2 puntos de diferencia** al llegar al final.
4.  **GOLDEN GOAL Animation:** Activa/Desactiva la cinemática de advertencia cuando se llega a un 5-5 (o punto crítico).
5.  **Re-rolls (Yellow/Orange):** Si un jugador tiene el poder Amarillo o Naranja guardado y golpea la pelota 2 veces sin activarlo, el poder cambia automáticamente a otro al azar.
6.  **All Re-roll (Red/Green):** Extiende la mecánica de cambio automático a los poderes Rojo y Verde.
7.  **Equal Watches / Powers:** Iguala las probabilidades de aparición al 20% para relojes y 25% para poderes (eliminando la rareza del Naranja).
8.  **The watches are kept:** Si se activa, capturar un reloj nuevo **no cancela** el efecto de zona activo del oponente. Permite que ambos jugadores tengan zonas activas simultáneamente.
9.  **Watch spawn frequency:** Hits globales necesarios para que aparezca un reloj (`[3, 5, 10, 15]`).
10. **Power spawn frequency:** Hits individuales de cada paleta para recibir un poder (`[3, 5, 7, 10, 12]`).
11. **Remove a watch/power:** Menús desplegables para prohibir la aparición de elementos específicos.

### Pestaña "EXTRAS" (Experimental Features)
1.  **Enable Orange Watch:** Permite la aparición del reloj naranja que activa el efecto Demolition Ball al impacto.
2.  **Enable MAG|NET Power:** Habilita el poder de atracción magnética.
3.  **Random GOLDEN Goal:** 10% de probabilidad por ronda de que el próximo gol gane la partida inmediatamente.

---

## 5. Enciclopedia de Poderes (v3.5)

*   **FIREBALL (Rojo):** Duplica la velocidad actual de la pelota (`speed * 2`) y la enciende en llamas. El efecto dura hasta que el rival la devuelve.
*   **SHIELD (Verde):** La paleta duplica su altura. Protege contra 3 impactos antes de encogerse. *Regla especial:* Mientras esté activo, los golpes no cuentan para el siguiente poder.
*   **SPEED (Amarillo):** Aumenta la velocidad de desplazamiento de la paleta en un 50%. Es acumulable y dura hasta el próximo gol.
*   **DEMOLITION (Naranja):** La pelota se vuelve gigante. Rebota en los bordes laterales (no hay gol normal). Si la paleta rival la toca, esta "explota" y el punto va para el atacante.
*   **MAGNET (Gris):** Atrae la pelota hacia el centro de la paleta cuando está en el campo del jugador, permitiendo teledirigir el disparo.

---

## 6. Enciclopedia de Relojes (Items de Campo)

*   **Azul (Cámara Lenta):** Crea una zona en tu campo que reduce la velocidad de la pelota al 50%.
*   **Rojo (Aceleración):** Zona de trampa que aumenta la velocidad de la pelota un 25% en tu campo.
*   **Violeta (Amnesia):** Resetea los hits del rival y lo obliga a usar sus poderes en máximo 2 toques o mutarán.
*   **Blanco (Muro):** Crea una barrera total de 5 rebotes. Si el rival sobrevive a los 5, recibe un poder de regalo. *Regla especial:* Mientras esté activo, el spawn de otros relojes se congela.
*   **Amarillo (Vida Extra):** Crea una barrera al fondo de la cancha. Si la pelota pasa la paleta, rebota en la barrera y se salva el punto. *Sonido: vida.wav*.
*   **Naranja (Instant Chaos):** Activa el efecto de la pelota gigante (Demolition) para quien lo golpee.

---

## 7. Estética y Sistema de Visualización
*   **Color GOLD:** `(255, 200, 0)`. Reservado para "GOLDEN GOAL" y textos de victoria especiales.
*   **Sistema de Tooltips:** Al posicionar el mouse sobre un modificador, se despliega una caja blanca con texto negro detallando su uso técnico.
*   **Rich Text Rendering:** El motor detecta palabras clave en los strings (como "RED", "BLUE", "GOLD") y les asigna su color correspondiente de forma automática durante el renderizado.

---

## 8. Lógica de Versionado (SemVer)
El proyecto utiliza un sistema de tres dígitos `X.Y.Z` para el seguimiento del progreso:
*   **X (Lanzamiento)**: Se mantiene en `0` durante el desarrollo. Pasará a `1.0.0` en el lanzamiento oficial.
*   **Y (Adiciones Grandes)**: Se incrementa cuando se añaden múltiples poderes, relojes o sistemas de modificadores complejos (ej: de `0.2.x` a `0.3.x`).
*   **Z (Cambios Pequeños)**: Se incrementa para arreglos de bugs, optimizaciones o la implementación de una sola mejora puntual (ej: de `0.3.0` a `0.3.1`).
