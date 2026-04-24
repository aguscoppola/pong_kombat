# Registro de Cambios (Changelog)

Aquí guardaremos una lista de todas las cosas nuevas que le vayamos agregando al juego o los errores que vayamos arreglando. Así no nos olvidamos de nada y cualquier persona que vea el proyecto sabrá en qué estuvimos trabajando.

## [2.0.0] - 2026-04-23
### Agregado (Nuevas cosas)
- ¡Implementación oficial del Modo Kombat! 
- Sistema de Poderes: Los jugadores obtienen un poder al azar (ofensivo o defensivo) tras acumular 7 toques.
- Poder Bola de Fuego (Paleta Roja): El próximo golpe duplica la velocidad de la pelota, la cual se enciende en llamas.
- Poder Escudo Gigante (Paleta Verde): La paleta duplica su tamaño por el tiempo que duren los próximos 2 golpes.
- Nuevo sistema de Sonidos Generativos: Añadido pitido retro para la pared, sonido "Pop" para la paleta, y un efecto de viento/fuego infinito para la bola de fuego.
- Organización Profesional: Se creó la carpeta `sounds/` dedicada exclusivamente a guardar recursos de audio.

### Cambiado (Ajustes de Balance)
- Reducidos los toques necesarios para obtener un poder de 10 a 7 (el juego es más dinámico).
- Mejora de controles: El Jugador 2 ahora usa la `Flecha Derecha` para activar sus poderes (antes era la L).
- El sonido del fuego ahora tiene el volumen a la mitad (50%) y un efecto de "Fade Out" de 0.5 segundos al desaparecer.

### Arreglado (Solución de Errores - Bugs)
- Solucionado el "Efecto Ametralladora" de sonido cuando la pelota rozaba el techo o piso (se agregó un cooldown de 0.25s).
- Solucionado el "Choque Fantasma" del Escudo Gigante: ahora la paleta espera 0.1s antes de volver a achicarse para permitir que la matemática del rebote termine bien.

## [1.0.0] - 2026-04-23
### Agregado (Nuevas cosas)
- ¡Nace el proyecto Pong Kombat!
- Creamos la estructura básica del juego y la pantalla.
- Añadimos las dos paletas (controlables con el teclado) y la pelota.
- Creamos el sistema de "físicas": la pelota rebota en las paredes y en las paletas cambiando de ángulo.
- Añadimos la puntuación: el juego termina cuando alguien llega a 12 puntos.
- Añadimos una pantalla de Menú para empezar el juego y otra de Fin de Juego (Game Over) para poder reiniciar.
