# Pong Kombat 🏓🔥

¡El clásico juego de "Pong", pero transformado en una batalla épica de reflejos y estrategia!

## ¿De qué trata?
Actualmente estamos en la **Versión 3.0 (Modo Kombat Definitivo)**. Hemos llevado el Pong original a otro nivel con poderes especiales, zonas de control temporal, un sistema de modificadores de partida y una identidad visual renovada. ¡Cada partida es única!

## Cómo instalar y jugar
1. Necesitas tener Python instalado (recomendamos la versión 3.12).
2. Abre tu terminal en la carpeta del juego e instala la librería de gráficos con:
   ```bash
   python -m pip install pygame-ce
   ```
3. Inicia el juego escribiendo:
   ```bash
   python3.12 main.py
   ```

## Controles 🎮
*   **Jugador 1 (Izquierda):** Movimiento con `W` (Subir) y `S` (Bajar). **Activar Poder:** Tecla `D`.
*   **Jugador 2 (Derecha):** Movimiento con `Flecha Arriba` y `Flecha Abajo`. **Activar Poder:** `Flecha Derecha`.
*   **Navegación:** Usa el **Mouse** para moverte por los menús y el panel de modificadores.
*   **Reiniciar/Back:** Tecla `Esc` o el botón de "Back" en pantalla.

## Mecánicas Especiales (Modo Kombat) 🔥
A medida que golpeas la pelota, acumulas "toques". Al llegar a la cantidad necesaria, obtendrás un poder aleatorio (tu paleta cambiará de color):

1. **Bola de Fuego (Paleta Roja):** Tu próximo golpe triplica la velocidad de la pelota. ¡Quema al rival!
2. **Escudo Gigante (Paleta Verde):** Tu paleta crece al doble de su tamaño original durante 2 golpes.
3. **Velocista (Paleta Amarilla):** Aumenta tu velocidad de movimiento un 50%. ¡Es acumulable!
4. **Bola de Demolición (Paleta Naranja):** ¡NUEVO! La pelota se vuelve gigante y un 50% más rápida. ¡Muy difícil de atajar!

*   **Reroll de Poder:** Si no activas un poder tras varios golpes, éste cambiará automáticamente a otro tipo.

## Ítems de Campo (Relojes de Arena) ⏳
Cada cierta cantidad de toques (configurables), aparecerá un **Reloj de Arena** en el centro. Captúralo para activar efectos en tu zona:

*   **Reloj Azul:** Zona de cámara lenta. La pelota viaja un 50% más lento en tu mitad.
*   **Reloj Rojo:** Zona de maldición. La pelota viaja un 25% más rápido. ¡Peligro!
*   **Reloj Violeta:** Zona de carga rápida. Solo necesitas 3 toques para obtener poderes.
*   **Reloj Amarillo (Crucifijo):** Genera una barrera divina detrás de ti que te salva de un gol.
*   **Reloj Blanco (Muro Absoluto):** ¡EL PODER DEFINITIVO! Tu mitad de cancha se convierte en una paleta gigante durante 5 toques.

## Panel de Modificadores ⚙️
Desde el menú principal puedes acceder a los **Match Modifiers** para personalizar tu experiencia:
*   **Score Limit:** Define cuántos puntos se necesitan para ganar.
*   **Match Point:** Activa la regla de "ganar por 2" con animaciones épicas.
*   **The Watches are Kept:** Permite que ambos jugadores tengan zonas activas al mismo tiempo.
*   **Spawn Taps:** Configura cada cuántos golpes aparece un nuevo reloj.
*   **Remove Watches:** Desactiva específicamente los relojes que no quieras en tu partida.

---
¡Prepárate para el Kombat! 🏓🔥
