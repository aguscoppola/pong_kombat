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
    "match_point": [
        "If both players are one point away from winning (5-5),",
        "the match will not end until one player gains a 2-point lead."
    ],
    "golden_goal_anim": [
        "Shows a golden warning during critical moments",
        "or sudden death rounds."
    ],
    "reroll": [
        "The orange and yellow power-ups will change into",
        "another power-up after 2 hits."
    ],
    "equal_watches": [
        "All watches have a 20% chance of appearing."
    ],
    "equal_powers": [
        "All power-ups (Red, Green, Yellow, Orange)",
        "have a 25% chance of appearing."
    ],
    "watches_kept": [
        "Picking up a new watch DOES NOT cancel",
        "the opponent's active zone effect."
    ],
    "watch_spawn": [
        "How many paddle hits are needed",
        "to spawn a random Watch on the field."
    ],
    "power_spawn": [
        "How many paddle hits are needed",
        "to grant a random power-up directly."
    ],
    "start_with_power": [
        "Both players start each round with a",
        "random power-up if enabled."
    ],
    "remove_power_menu": ["Expand to disable specific paddle powers."],
    "remove_power_red": ["Fireball Power will never appear."],
    "remove_power_green": ["Giant Shield Power will never appear."],
    "remove_power_yellow": ["Speed Power will never appear."],
    "remove_power_orange": ["Demolition Ball Power will never appear."],
    "floating_planets": [
        "Adds two planets that attract the ball with gravity.",
        "They are placed at the top and bottom of the court."
    ],
    "gravity_force": [
        "Adjusts the attraction force of the planets.",
        "Higher values will curve the ball's path more sharply."
    ],
    "gravity_radius": [
        "Adjusts the reach of the planetary gravity.",
        "Defines how close the ball must be to be attracted."
    ],
    "destructible_planets": [
        "Planets can be destroyed if they are hit by the ball.",
        "They will explode and respawn in the next round."
    ],
    "planet_resistance": [
        "Sets how many hits a planet can take before exploding.",
        "Based on the astronomical hierarchy (Moon to Star)."
    ],
    "orange_watch": [
        "Orange Watch: If hit by the ball, it triggers",
        "the Demolition Ball effect instantly!"
    ],
    "magnet_power": [
        "MAGNET: The ball is attracted to your paddle",
        "center like a planet when in your zone.",
        "Allows steering the ball after hitting it."
    ],
    "exp_golden_goal": [
        "Random GOLDEN Goal: 10% chance per round",
        "to become Sudden Death. Next goal wins the match!"
    ],
    "x2_multiplier": [
        "X2 Multiplier: 50% chance to spawn an X2 icon at the start.",
        "Appears after the first hit. Capturing it turns the ball GOLD",
        "and the next goal will be worth 2 points."
    ],
    "ghost_power": [
        "GHOST: Shoot 1 spectral ball that the rival must catch.",
        "Ghost balls are 50% slower. If they leave the screen",
        "behind the opponent, you score a point!"
    ],
    "add_mouse": [
        "Adds a mouse that tries to eat the ball (cheese).",
        "If it succeeds, the last hitter loses 1 point.",
        "The mouse enters after the second bounce."
    ],
    "encapsulate_powers": [
        "Stores your current power in your score number",
        "when receiving a new one. It activates automatically",
        "once your paddle is free and effects are over."
    ]
}
