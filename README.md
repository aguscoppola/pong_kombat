# Pong Kombat 🏓🔥

¡El clásico juego de "Pong", pero con algunas mecánicas nuevas y picantes!

## ¿De qué trata?
Actualmente estamos en la **Versión 2.5 (Modo Kombat Avanzado)**. Partiendo de la base clásica de Pong, hemos añadido nuevas mecánicas de pelea, poderes especiales acumulables, mecánicas de "robo de zonas" (Tira y Afloja), y sonidos inmersivos para darle mucha más acción a cada partida. ¡El primero en anotar 6 puntos gana!

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
*   **Empezar/Reiniciar:** Barra Espaciadora.

## Mecánicas Especiales (Modo Kombat) 🔥
A medida que los jugadores golpean la pelota, acumulan "toques". **Al llegar a los 7 toques**, el jugador obtendrá aleatoriamente uno de estos TRES poderes (su paleta cambiará de color para avisarle):
1. **Bola de Fuego (Paleta Roja):** Al activarlo, tu próximo golpe convertirá la pelota en una bola de fuego que viaja al **doble de velocidad** hasta que el rival logre atajarla.
2. **Escudo Gigante (Paleta Verde):** Al activarlo, tu paleta crecerá al **doble de su tamaño** original, haciéndote casi invencible durante los próximos 2 golpes.
3. **Velocista (Paleta Amarilla):** Aumenta tu velocidad de movimiento un **50% extra**. Es acumulable y dura hasta el próximo gol. ¡Si no lo activas durante 2 golpes, la paleta hará un "Reroll" y cambiará al poder Rojo o Verde!

## Ítems de Campo (El Reloj de Arena) ⏳
A los 10 toques globales, y luego cada 5 toques adicionales, aparecerá un **Reloj de Arena** en el centro. El jugador que haya golpeado la pelota justo antes de que ésta toque el reloj, obtendrá una Zona de control en su mitad de la cancha:
* **Reloj Azul (75%):** La pelota viaja un 50% más lento en tu mitad de la cancha. ¡Ideal para defender!
* **Reloj Rojo (25%):** Maldición. La pelota viaja un 25% más rápido en tu mitad de la cancha. ¡Esquívalo!
* **Robo de Zonas:** ¡Cada nuevo reloj que aparece permite robarle la zona a tu rival o cambiar tu maldición!
