# Pong Kombat - Documento de Especificaciones Técnicas (v0.5.0)

## 1. Visión General
**Pong Kombat** es una evolución del clásico arcade que introduce mecánicas de combate, gestión de poderes y alteración del entorno mediante ítems. El juego está construido sobre un motor de físicas AABB personalizado en Python con `pygame-ce`.

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
*   **SETTINGS**: Acceso desde el menú principal para configurar sonido e idioma.

### Modo SOLO (IA)
*   **IA Táctica**: La computadora busca pelotas, esquiva amenazas (naranjas/balas), utiliza portales para anticiparse y gestiona sus poderes de forma agresiva.
*   **Aiming (Revolver)**: La IA alineará su centro con la paleta del jugador para disparar con precisión.

---

## 3. Mecánicas del Core Engine

### Físicas de Rebote (Ángulo Dinámico)
El ángulo de salida de la pelota se calcula según el punto de impacto en la paleta:
*   **Fórmula:** `ángulo = (distancia_al_centro / (altura_paleta / 2)) * MAX_BOUNCE_ANGLE`
*   **Resultado:** Golpear con los extremos da ángulos cerrados; el centro dispara de forma horizontal.

### Gestión de Velocidad (v0.3.4)
1.  **Initial Speed:** Velocidad base al sacar (`x0.75` hasta `x2.0 FLASH`).
2.  **Speed Increase:** Aceleración acumulativa tras cada rebote (`0.01` a `0.075`).
3.  **Dimensional Boost (NEW):** Cada paso por un **PORTAL** aumenta la velocidad total un **0.5%** y rota la trayectoria **5 grados**.

---

## 4. Diccionario de Modificadores (Match Modifiers)

### Pestaña "ALL" (Configuración Global)
1.  **Score Limit:** Puntuación para ganar (`3, 6, 9`).
2.  **Ball Speed Increase:** Incremento por hit.
3.  **Initial Ball Speed:** Velocidad de saque.
4.  **MATCH POINT:** Regla de ventaja de 2 puntos para ganar.
5.  **Spawn Frequencies:** Hits necesarios para relojes y poderes.

### Pestaña "EXTRAS" (Mecánicas Avanzadas)
*   **PORTALS System (The Portal Update):** 
    *   **Logic:** Teletransporte instantáneo entre pares de colores (Azul <-> Naranja, Rojo <-> Verde).
    *   **Safety:** Sistema `last_portal_id` para evitar bucles infinitos.
    *   **PORTAL size:** 5 niveles: Minion (25px), Short (50px), Default (75px), Big (125px), Giant (200px).
    *   **Orientation:** Toggle entre horizontal (muros superior/inferior) y vertical (postes laterales).
    *   **2 more PORTALS:** Activa los portales Rojo y Verde con conexión cruzada.
*   **Allow Floating Planets:** Añade astros con gravedad física (Moon, Planet, Star).
*   **Add a MOUSE:** Introduce un pequeño ratón que interfiere en el campo.
    *   **Initial mouse speed:** Niveles de velocidad ajustables.
    *   **Appear timer:** Segundos de retraso para su aparición.
*   **X2 Multiplier:** Ítem dorado que duplica el valor del gol.
*   **Ghost Power:** Dispara proyectiles espectrales lentos.
*   **Magnet Power:** Atrae la pelota hacia la paleta.
*   **REVOLVER (The Combat Update):** 
    *   **Logic:** Ítem orbital que otorga 3 disparos letales.
    *   **Precision:** Trayectoria recta horizontal con seguro de disparo de 0.1s.
    *   **Spawn:** 25% de probabilidad al aparecer cualquier reloj.
*   **GUM Power (The Sticky Update):** 
    *   **Logic:** Adherencia de pelotas y disparos de chicle erráticos.

### Pestaña "SKINS"
*   **Change ORANGE power:** Skins "Default" y "Hadouken".
*   **Change YELLOW watch:** Skins "Default" y "CROSS".

---

## 5. Enciclopedia de Poderes
*   **FIREBALL (Rojo):** Duplica la velocidad y enciende la pelota.
*   **SHIELD (Verde):** Paleta doble altura (3 impactos).
*   **SPEED (Amarillo):** +50% velocidad de movimiento.
*   **DEMOLITION (Naranja):** Pelota gigante y rebotes laterales.
*   **MAGNET (Gris):** Control de trayectoria.
*   **GHOST (Blanco Azulado):** Proyectil señuelo.
*   **REVOLVER (Gris/Marrón):** Sistema de disparos amarillos letales.
*   **GUM (Rosa):** Adherencia y proyectiles de chicle.

---

## 6. Enciclopedia de Relojes
*   **Azul:** Zona de cámara lenta.
*   **Rojo:** Zona de trampa (aceleración).
*   **Violeta:** Carga rápida de poderes.
*   **Blanco:** Muro absoluto.
*   **Amarillo:** Vida Extra / Barrera trasera.
*   **Naranja:** Instant Demolition.

---

## 7. Estética y UI
*   **Rich Text:** Soporte para colores dinámicos (`|COLOR|`) en etiquetas.
*   **Top-Layer Tooltips:** Ayudas informativas que siempre aparecen en la capa superior.
*   **Text-Only Tooltips:** Activación de ayuda solo mediante el texto de las opciones para mayor limpieza visual.

---

## 8. Lógica de Versionado (SemVer)
*   **v0.4.0**: "The Solo & Settings Update" - Modo contra IA y panel de ajustes (Volumen, Idioma, Shake).
*   **v0.5.0**: "The REVOLVER Update" - Combate letal, IA pistolera, poder de chicle y estabilidad de efectos visuales.
