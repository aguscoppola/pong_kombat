# Registro de Cambios (Changelog)

Aquí guardaremos una lista de todas las cosas nuevas que le vayamos agregando al juego o los errores que vayamos arreglando. Así no nos olvidamos de nada y cualquier persona que vea el proyecto sabrá en qué estuvimos trabajando.

## [3.0.0] - 2026-05-02
### ¡LA GRAN ACTUALIZACIÓN KOMBAT!
Esta versión transforma el juego por completo, añadiendo profundidad táctica, una interfaz renovada y mucho más carisma.

#### Agregado (Nuevas cosas)
- **Nuevo Poder de Paleta: "Bola de Demolición" (Naranja)**. Aumenta el tamaño de la pelota al doble y su velocidad un 50%. ¡Ideal para confundir al rival!
- **Nuevos Relojes de Arena (Mecánicas de Campo)**:
    - **Reloj Violeta (Zona de Velocidad)**: Reduce los toques necesarios para cargar poderes de 7 a solo 3. ¡Carga rápida activada!
    - **Reloj Amarillo (Vida Extra / Crucifijo)**: Crea una barrera divina detrás de tu paleta que te salva de un gol seguro.
    - **Reloj Blanco (Muro Absoluto)**: El poder definitivo. Convierte toda tu mitad de la cancha en una paleta gigante invencible durante 5 toques.
- **Nuevo Sistema de Menús**:
    - **Menú Principal**: Interfaz limpia con títulos dinámicos y acceso rápido.
    - **Panel de Modificadores (Match Modifiers)**: Un centro de control con scroll para personalizar cada aspecto de la partida.
    - **Tooltips Dinámicos**: Pasa el ratón por encima de cualquier modificador para ver una explicación detallada de su funcionamiento.
- **Nuevos Modificadores de Partida**:
    - **The Watches are Kept**: Las zonas de los jugadores ya no se cancelan entre sí. ¡Caos de colores simultáneo!
    - **Taps for Next Watch**: Configura cuántos golpes deben pasar para que aparezca un reloj (1, 3, 5, 10 o 15).
    - **Equal Power-ups**: Probabilidades equilibradas (25%) para todos los poderes.
    - **Match Point (Win by 2)**: Animación épica de "MATCH POINT" con movimiento suavizado y sonido de campanas de boxeo.
- **Sonido y Estética**:
    - **Efectos de Sonido**: Añadidos sonidos de "Hit" (golpe seco) y "Pop" (burbuja) para botones e interacciones.
    - **Pixel Art**: Reloj de arena rediseñado con estética retro de píxeles.
    - **Capa de Interfaz**: Marcadores inteligentes que cambian de color (blanco/negro) según el fondo para ser siempre legibles.

#### Arreglado (Bugs y Pulido)
- Corregido el bug donde los poderes se cancelaban de forma extraña.
- Optimizada la aparición de relojes para evitar solapamientos con el Muro Blanco.
- Mejorada la lógica de Deuce (empate) para que la animación de Match Point sea precisa en cualquier puntaje.

## [2.5.0] - 2026-04-24
### Agregado (Nuevas cosas)
- Nuevo Poder de Paleta: "Velocista" (Color Amarillo). Aumenta la velocidad de movimiento de la paleta un 50%.
- Sistema de Poder Acumulativo: El poder amarillo no tiene límite de tiempo y se puede apilar (hasta +100% de velocidad o más) si logras sacarlo dos veces en la misma ronda sin que te anoten un gol.
- Nueva Mecánica de "Reroll": Si obtienes el poder Amarillo pero decides no activarlo, tras golpear la pelota 2 veces, se transformará aleatoriamente en el Rojo o en el Verde.
- Nuevo Ítem de Campo: El "Reloj de Arena". Aparece en el centro del campo a los 10 toques globales, y luego reaparece/re-sortea cada 5 toques (15, 20, 25...).
- Zona de Cámara Lenta (Reloj Azul): 75% de probabilidad de aparición. Al tocarlo, el dueño de la zona verá la velocidad de la pelota reducida a la mitad (50%) en su mitad de la cancha. Acompañado de fanfarria estilo "Zelda".
- Zona de Maldición (Reloj Rojo): 25% de probabilidad de aparición. Aumenta la velocidad de la pelota un 25% (x1.25) en la mitad de la cancha del jugador afectado. Acompañado de un sonido de "Acceso Denegado".
- Mecánica de "Robo de Zona" (Tira y Afloja): Como el reloj reaparece cada 5 toques, un jugador en desventaja puede intentar capturar el nuevo reloj para robarle la zona a su oponente.

### Cambiado (Ajustes de Balance)
- Las rondas ahora son más cortas e intensas: el ganador es el primero en llegar a 6 puntos (antes 12).
- Se redujo el incremento de velocidad de la pelota por cada toque a un 2.5% (multiplicador de 1.025) para permitir rondas más largas y favorecer la acumulación de poderes y relojes.
- Se ha actualizado la versión del Menú Principal a "PONG KOMBAT v2.5".

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
