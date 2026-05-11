import pygame

# --- Dimensiones ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15

# --- Configuración de Juego ---
FPS = 60
PADDLE_SPEED = 400
MAX_BOUNCE_ANGLE = 60 # Grados

# --- Colores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
ORANGE = (255, 120, 0)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
PINK = (255, 182, 193)
GHOST_COLOR = (150, 200, 255)

# Colores de Zonas
BLUE_ZONE = (0, 0, 100)
RED_ZONE = (100, 0, 0)
VIOLET_ZONE = (80, 0, 80)
WHITE_ZONE = (200, 200, 200)

# --- Estados del Juego ---
STATE_MAIN_MENU = "main_menu"
STATE_MODIFIERS = "modifiers"
STATE_SERVE = "serve"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_PRESS_TO_START = "press_to_start"
STATE_SETTINGS = "settings"
STATE_MODE_SELECTION = "mode_selection"
STATE_SOLO_SUBMODE_SELECTION = "solo_submode_selection"
STATE_ARCADE_LEVEL_START = "arcade_level_start"
STATE_ARCADE_REWARD = "arcade_reward"
STATE_ARCADE_TUTORIAL = "arcade_tutorial"

# --- Tipos de Poderes ---
POWER_NONE = 0
POWER_FIREBALL = 1
POWER_SHIELD = 2
POWER_SPEED = 3
POWER_MAGNET = 4
POWER_ORANGE = 5
POWER_GHOST = 6
POWER_GUM = 7
POWER_REVOLVER = 8
POWER_SLEEP = 9

GUM_PINK = (255, 105, 180) 
SLEEP_PURPLE = (180, 0, 255)
LIGHT_BROWN = (181, 101, 29)
GUN_METAL = (128, 128, 128)
