# Pong Kombat - Definiciones de Pixel Art y Assets Visuales

# --- Planetas (9x9) ---
PLANET_MATRIX = [
    [0,0,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,0,0],
]

# --- Reloj de Arena (9x7) ---
HOURGLASS_MATRIX = [
    [1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1],
    [0,1,1,1,1,1,0],
    [0,0,1,1,1,0,0],
    [0,0,0,1,0,0,0],
    [0,0,1,1,1,0,0],
    [0,1,1,1,1,1,0],
    [1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1],
]

# --- Cruz Bíblica (10x8) ---
CROSS_MATRIX = [
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,0,1,1,0,0,0],
]

# --- Ícono Multiplicador X2 ---
X2_MATRIX_X = [
    [1,0,0,0,1],
    [0,1,0,1,0],
    [0,0,1,0,0],
    [0,1,0,1,0],
    [1,0,0,0,1]
]

X2_MATRIX_2 = [
    [1,1,1,1,1],
    [0,0,0,0,1],
    [1,1,1,1,1],
    [1,0,0,0,0],
    [1,1,1,1,1]
]

# --- Configuración de Tooltips ---
TOOLTIPS = {
    "EN": {
        "match_point": ["If both players are one point away from winning (5-5),", "the match will not end until one player gains a 2-point lead."],
        "golden_goal_anim": ["Shows a golden warning during critical moments", "or sudden death rounds."],
        "reroll": ["The orange and yellow power-ups will change into", "another power-up after 2 hits."],
        "equal_watches": ["All watches have a 20% chance of appearing."],
        "equal_powers": ["All power-ups (Red, Green, Yellow, Orange)", "have a 25% chance of appearing."],
        "watches_kept": ["Picking up a new watch DOES NOT cancel", "the opponent's active zone effect."],
        "watch_spawn": ["How many paddle hits are needed", "to spawn a random Watch on the field."],
        "power_spawn": ["How many paddle hits are needed", "to grant a random power-up directly."],
        "start_with_power": ["Both players start each round with a", "random power-up if enabled."],
        "remove_power_menu": ["Expand to disable specific paddle powers."],
        "remove_power_red": ["Fireball Power will never appear."],
        "remove_power_green": ["Giant Shield Power will never appear."],
        "remove_power_yellow": ["Speed Power will never appear."],
        "remove_power_orange": ["Demolition Ball Power will never appear."],
        "floating_planets": ["Adds two planets that attract the ball with gravity.", "They are placed at the top and bottom of the court."],
        "gravity_force": ["Adjusts the attraction force of the planets.", "Higher values will curve the ball's path more sharply."],
        "gravity_radius": ["Adjusts the reach of the planetary gravity.", "Defines how close the ball must be to be attracted."],
        "destructible_planets": ["Planets can be destroyed if they are hit by the ball.", "They will explode and respawn in the next round."],
        "planet_resistance": ["Sets how many hits a planet can take before exploding.", "Based on the astronomical hierarchy (Moon to Star)."],
        "orange_watch": ["Orange Watch: If hit by the ball, it triggers", "the Demolition Ball effect instantly!"],
        "magnet_power": ["MAGNET: The ball is attracted to your paddle", "center like a planet when in your zone.", "Allows steering the ball after hitting it."],
        "exp_golden_goal": ["Random GOLDEN Goal: 10% chance per round", "to become Sudden Death. Next goal wins the match!"],
        "x2_multiplier": ["X2 Multiplier: 50% chance to spawn an X2 icon at the start.", "Appears after the first hit. Capturing it turns the ball GOLD", "and the next goal will be worth 2 points."],
        "ghost_power": ["GHOST: Shoot 1 spectral ball that the rival must catch.", "Ghost balls are 50% slower. If they leave the screen", "behind the opponent, you score a point!"],
        "add_mouse": ["Adds a mouse that tries to eat the ball (cheese).", "If it succeeds, the last hitter loses 1 point.", "The mouse enters after the second bounce."],
        "encapsulate_powers": ["Stores your current power in your score number", "when receiving a new one. It activates automatically", "once your paddle is free and effects are over."],
        "portals": ["Adds dimensional PORTALS on floor and ceiling.", "The ball enters one and exits from the other."],
        "portal_size": ["Change the length of the PORTALS."],
        "portals_vertical": ["Flip PORTALS to vertical orientation on the side walls."],
        "more_portals": ["Add RED and GREEN PORTALS (Cross-connection)."],
        "revolver": ["REVOLVER: Orbiting item at center.", "Allows shooting 3 BULLETS that destroy", "the enemy paddle temporarily."],
        "gum_power": ["GUM: The ball sticks to your paddle!", "You have 3 seconds to aim and shoot.", "Consumes charges per second."],
        "start_x2": ["X2 Multiplier: 50% initial chance.", "After first hit, capture the icon to make", "the next goal worth 2 points."],
        "sleeping_power": ["SLEEP: Shoots a large violet projectile that", "splits into 3 at mid-map.", "Immobilizes opponent for 2 hits if caught."],
        "cloudy_day": ["CLOUDY DAY: Random clouds will cross the field.", "They are 100% opaque, covering ball and paddles.", "They speed up exponentially after 30 hits!"],
        "rainy_day": ["RAINY DAY: Falls small raindrops across the court.", "They are in the same layer as clouds,", "so they cover paddles, ball, and powers!"],
        "lightning": ["LIGHTNING: 5% chance per second of a full-screen flash.", "Blinds the screen, fading back to normal over 0.5s.", "Accompanied by a realistic thunder sound effect!"]
    },
    "ES": {
        "match_point": ["Si ambos jugadores están a un punto de ganar (5-5),", "la partida no terminará hasta que haya 2 puntos de ventaja."],
        "golden_goal_anim": ["Muestra una advertencia dorada en momentos", "críticos o rondas de muerte súbita."],
        "reroll": ["Los poderes naranja y amarillo cambiarán a otro", "poder aleatorio tras 2 golpes."],
        "equal_watches": ["Todos los relojes tienen un 20% de probabilidad."],
        "equal_powers": ["Todos los poderes tienen un 25% de probabilidad."],
        "watches_kept": ["Recoger un nuevo reloj NO cancela", "el efecto de zona activo del oponente."],
        "watch_spawn": ["Cuántos golpes de paleta se necesitan para", "que aparezca un reloj aleatorio en el campo."],
        "power_spawn": ["Cuántos golpes se necesitan para recibir", "un poder aleatorio directamente."],
        "start_with_power": ["Ambos jugadores comienzan cada ronda con", "un poder aleatorio si está activado."],
        "remove_power_menu": ["Expande para desactivar poderes específicos."],
        "remove_power_red": ["El poder de Bola de Fuego nunca aparecerá."],
        "remove_power_green": ["El Escudo Gigante nunca aparecerá."],
        "remove_power_yellow": ["El poder de Velocidad nunca aparecerá."],
        "remove_power_orange": ["La Bola de Demolición nunca aparecerá."],
        "floating_planets": ["Añade dos planetas que atraen la bola con gravedad.", "Se sitúan arriba y abajo de la pista."],
        "gravity_force": ["Ajusta la fuerza de atracción de los planetas.", "Valores altos curvan más la trayectoria."],
        "gravity_radius": ["Ajusta el alcance de la gravedad planetaria.", "Define a qué distancia se atrae la bola."],
        "destructible_planets": ["Los planetas pueden destruirse si reciben golpes.", "Explotarán y reaparecerán en la siguiente ronda."],
        "planet_resistance": ["Define cuántos golpes aguanta un planeta.", "Basado en jerarquía (Luna hasta Estrella)."],
        "orange_watch": ["Reloj Naranja: ¡Si la bola lo toca, activa", "la Bola de Demolición al instante!"],
        "magnet_power": ["IMÁN: La bola es atraída al centro de tu paleta", "como un planeta. Permite dirigir el tiro."],
        "exp_golden_goal": ["Gol de Oro aleatorio: 10% de probabilidad", "de muerte súbita. ¡El próximo gol gana!"],
        "x2_multiplier": ["Multiplicador de X2: 50% de probabilidad inicial.", "Tras el primer golpe, captura el ícono para que", "el próximo gol valga 2 puntos."],
        "ghost_power": ["FANTASMA: Lanza 1 bola espectral lenta.", "Si el rival no la atrapa y sale del campo,", "¡marcas un punto!"],
        "add_mouse": ["Añade un ratón que intenta comerse la bola.", "Si lo logra, el último en tocarla pierde 1 punto.", "Entra tras el segundo rebote."],
        "encapsulate_powers": ["Guarda tu poder actual en tu marcador al recibir", "uno nuevo. Se activa automáticamente al quedar libre."],
        "portals": ["Añade PORTALES dimensionales en techo y suelo.", "La bola entra por uno y sale por el otro."],
        "portal_size": ["Cambia la longitud de los PORTALES."],
        "portals_vertical": ["Gira los PORTALES a las paredes laterales."],
        "more_portals": ["Añade portales ROJOS y VERDES (Conexión cruzada)."],
        "revolver": ["REVÓLVER: Ítem que orbita el centro.", "Permite disparar 3 BALAS que destruyen", "la paleta enemiga temporalmente."],
        "gum_power": ["CHICLE: ¡La bola se queda pegada a tu paleta!", "Tienes 3 segundos para apuntar y disparar.", "Consume cargas por segundo."],
        "start_x2": ["Multiplicador de X2: 50% de probabilidad inicial.", "Tras el primer golpe, captura el ícono para que", "el próximo gol valga 2 puntos."],
        "sleeping_power": ["SUEÑO: Lanza un gran proyectil violeta que", "se divide en 3 al cruzar la mitad.", "Inmoviliza al rival por 2 toques si lo atrapa."],
        "cloudy_day": ["DÍA NUBLADO: Nubes aleatorias cruzan el campo.", "Son 100% opacas, tapando pelota y paletas.", "¡Se aceleran exponencialmente tras 30 golpes!"],
        "rainy_day": ["DÍA LLUVIOSO: Caen pequeñas gotas de lluvia en el campo.", "Están en la misma capa que las nubes,", "¡por lo que tapan paletas, pelota y poderes!"],
        "lightning": ["RELÁMPAGO: 5% de probabilidad por segundo de un destello.", "Ciega la pantalla, volviendo a la normalidad en 0.5s.", "¡Acompañado por el estruendo de un trueno!"]
    }
}
