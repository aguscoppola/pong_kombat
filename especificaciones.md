# Pong Kombat - Documento de Especificaciones Técnicas (v0.3.3)

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

---

## 3. Mecánicas del Core Engine

### Físicas de Rebote (Ángulo Dinámico)
El ángulo de salida de la pelota se calcula según el punto de impacto en la paleta:
*   **Fórmula:** `ángulo = (distancia_al_centro / (altura_paleta / 2)) * MAX_BOUNCE_ANGLE`
*   **Resultado:** Golpear con los extremos da ángulos cerrados; el centro dispara de forma horizontal.

### Gestión de Velocidad (v0.3.3)
1.  **Initial Speed:** Velocidad base al sacar (`x0.75` hasta `x2.0 FLASH`).
2.  **Speed Increase:** Aceleración acumulativa tras cada rebote (`0.01` a `0.075`).

---

## 4. Diccionario de Modificadores (Match Modifiers)

### Pestaña "ALL" (Configuración Global)
1.  **Score Limit:** Puntuación para ganar (`3, 6, 9`).
2.  **Ball Speed Increase:** Incremento por hit. Niveles: Low (0.01), Default (0.025), Original (0.05), Fast (0.075).
3.  **Initial Ball Speed:** Velocidad de saque. Niveles: Low, Default, Mid, Fast, FLASH.
4.  **MATCH POINT:** Regla de ventaja de 2 puntos para ganar.
5.  **GOLDEN Goal Animation:** Brillo dorado de advertencia en puntos críticos.
6.  **Re-rolls:** Los poderes Amarillo/Naranja mutan tras 2 hits si no se usan.
7.  **All Re-roll:** Extiende la mutación a los poderes Rojo/Verde.
8.  **Equal Watches / Powers:** Iguala las probabilidades de aparición.
9.  **Watches Kept:** Permite zonas activas simultáneas para ambos jugadores.
10. **Spawn Frequencies:** Hits necesarios para relojes y poderes.
11. **Remove watch/power:** Desactiva elementos específicos (Nombres en MAYÚSCULAS).

### Pestaña "EXTRAS" (Mecánicas Avanzadas)
*   **Allow Floating Planets:** Añade dos astros con gravedad física.
    *   **Jerarquía:** Moon, Planet (Tierra/Marte), Gas Giant (Júpiter/Saturno), Star.
    *   **Explosiones:** Partículas temáticas según el astro (Azul, Rojo, Beige, Tan, Amarillo, Gris).
*   **X2 Multiplier:** Aparece un ícono dorado; capturarlo duplica el valor del siguiente gol.
*   **Magnet Power Enabled:** Añade el Imán (Poder Gris) a la rotación.
*   **Random GOLDEN GOAL:** 15% de probabilidad de muerte súbita por ronda.

### Pestaña "SKINS" (Personalización v0.3.3)
*   **Change ORANGE power:** Skins "Default" y "Hadouken" (Color Cyan).
*   **Change YELLOW watch:** Skins "Default" y **"CROSS"** (Cruz Bíblica de madera marrón).

---

## 5. Enciclopedia de Poderes
*   **FIREBALL (Rojo):** Duplica la velocidad y enciende la pelota.
*   **SHIELD (Verde):** Paleta doble altura (3 impactos).
*   **SPEED (Amarillo):** +50% velocidad de movimiento de paleta.
*   **DEMOLITION (Naranja):** Pelota gigante y rebotes laterales.
*   **MAGNET (Gris):** Control de trayectoria teledirigida.

---

## 6. Enciclopedia de Relojes
*   **Azul:** Zona de cámara lenta (50%).
*   **Rojo:** Zona de trampa (+25% velocidad).
*   **Violeta:** Carga de poderes rápida (3 hits).
*   **Blanco:** Muro total de 5 rebotes.
*   **Amarillo:** Vida Extra / Barrera trasera. *Skin CROSS disponible*.
*   **Naranja:** Activación instantánea de Demolition.

---

## 7. Estética y UI
*   **V-Arrows:** Acordeones con flechas "V" dentro de cuadrados.
*   **Rich Text:** Soporte para colores dinámicos (`|COLOR|`) en textos.
*   **Audio Fix:** Buffer optimizado a 2048 para evitar ruidos en Windows.

---

## 8. Lógica de Versionado (SemVer)
*   **v0.3.3**: Versión actual de Pulido Estético y Mecánicas Planetarias.
