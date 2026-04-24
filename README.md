# Pong Kombat 🏓🔥

¡El clásico juego de "Pong", pero con algunas mecánicas nuevas y picantes!

## ¿De qué trata?
Actualmente estamos en la **Versión 2.0 (Modo Kombat)**. Partiendo de la base clásica de Pong, hemos añadido nuevas mecánicas de pelea, poderes especiales aleatorios, y sonidos inmersivos para darle mucha más acción a cada partida. ¡El primero en anotar 12 puntos gana!

## Cómo instalar y jugar
1. Necesitas tener Python instalado (recomendamos la versión 3.12).
2. Abre tu terminal en la carpeta del juego e instala la librería de gráficos con:
   ```bash
   python -m pip install pygame-ce
   ```
3. Inicia el juego escribiendo:
   ```bash
   python main.py
   ```

## Controles 🎮
*   **Jugador 1 (Izquierda):** Movimiento con `W` (Subir) y `S` (Bajar). **Activar Poder:** Tecla `D`.
*   **Jugador 2 (Derecha):** Movimiento con `Flecha Arriba` y `Flecha Abajo`. **Activar Poder:** `Flecha Derecha`.
*   **Empezar/Reiniciar:** Barra Espaciadora.

## Mecánicas Especiales (Modo Kombat) 🔥
A medida que los jugadores golpean la pelota, acumulan "toques". **Al llegar a los 7 toques**, el jugador obtendrá aleatoriamente uno de estos dos poderes (su paleta cambiará de color para avisarle):
1. **Bola de Fuego (Paleta Roja):** Al activarlo, tu próximo golpe convertirá la pelota en una bola de fuego que viaja al **doble de velocidad** hasta que el rival logre atajarla.
2. **Escudo Gigante (Paleta Verde):** Al activarlo, tu paleta crecerá al **doble de su tamaño** original, haciéndote casi invencible durante los próximos 2 golpes.
