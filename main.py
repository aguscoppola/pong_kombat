import pygame  # Importamos pygame, nuestra caja de herramientas para el juego.
import random  # Para las decisiones al azar (como el sorteo de poderes).
import sys     
import math    
import os      # Para manejar carpetas y rutas de archivos

# --- Constantes Básicas ---
SCREEN_WIDTH = 800   
SCREEN_HEIGHT = 600  
FPS = 60             

# ¡Agregamos colores nuevos para los poderes!
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)       
RED = (255, 50, 50)     # Rojo para la Bola de Fuego
GREEN = (50, 255, 50)   # Verde para el Escudo Gigante
YELLOW = (255, 255, 0)  # Amarillo para Velocista
ORANGE = (255, 128, 0)  # Naranja para el Espejismo
PURPLE = (180, 100, 255) # Violeta Claro para el Reloj y su Zona
VIOLET_ZONE = (100, 0, 150) # Versión para el fondo de la zona
BLUE = (0, 100, 255) # Azul para el Reloj Azul
CYAN = (0, 255, 255) # Para contenido experimental
GRAY = (150, 150, 150) # Para el poder IMAN
GOLD = (255, 200, 0) # Amarillo oscuro para el GOLDEN GOAL

# Constantes de los Poderes (para que el código sea más fácil de leer)
POWER_NONE = 0       # Sin poder
POWER_FIREBALL = 1   # Poder de Bola de Fuego
POWER_SHIELD = 2     # Poder de Paleta Gigante
POWER_SPEED = 3      # Poder Velocista (Amarillo)
POWER_ORANGE = 4     # ¡NUEVO! Poder Naranja (Espejismo)
POWER_MAGNET = 5     # ¡NUEVO! Poder IMAN (Gris)

# Cosas de las Paletas
PADDLE_WIDTH = 15      
PADDLE_HEIGHT = 100    
PADDLE_SPEED = 400     
PADDLE_OFFSET = 30     

# Cosas de la Pelota
BALL_SIZE = 15           
BALL_START_SPEED = 300   
BALL_SPEED_MULTIPLIER = 1.025 # Reducido para permitir rondas más largas (acumular poderes)
MAX_BOUNCE_ANGLE = math.radians(60) 

# Estados del Juego
STATE_MAIN_MENU = 0  
STATE_PLAYING = 1    
STATE_GAME_OVER = 2  
STATE_SERVE = 3      
STATE_PRESS_TO_START = 4
STATE_MODIFIERS = 5

# --- CLASES ---

class Paddle:
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.y_float = float(y)
        self.original_x = x        # Guardamos su posición original en X
        
        # ¡Nuevas variables para la v2.0 Kombat!
        self.color = WHITE         # La paleta empieza siendo blanca
        self.hits = 0              # Contador de toques (empieza en 0)
        self.power_stored = POWER_NONE # Poder guardado listo para usarse
        self.power_active = POWER_NONE # Poder que se está usando AHORA mismo
        self.shield_hits_left = 0  # Cuántos golpes le quedan al escudo gigante
        self.shield_shrink_timer = 0.0 # ¡NUEVO! Tiempo de espera antes de encogerse
        self.speed_multiplier = 1.0    # Acumulable: 1.0 (Normal), 1.5 (+50%), 2.0 (+100%)
        self.yellow_power_hits = 0     # Contador de golpes sin activar para el "Reroll" amarillo
        self.orange_power_hits = 0     # Contador de golpes sin activar para el "Reroll" naranja
        self.red_power_hits = 0        # Para el All Reroll
        self.green_power_hits = 0      # Para el All Reroll
        self.has_extra_life = False    # ¡NUEVO! Barrera amarilla (Crucifijo)

    # Función que reinicia la paleta cuando alguien anota un gol
    def reset(self):
        self.rect.height = PADDLE_HEIGHT # Vuelve al tamaño normal por las dudas
        self.rect.width = PADDLE_WIDTH   # Vuelve al ancho normal
        self.rect.x = self.original_x    # Vuelve a su posición original
        
        self.color = WHITE               # Vuelve a ser blanca
        self.hits = 0                    # ¡Los toques vuelven a 0!
        self.power_stored = POWER_NONE
        self.power_active = POWER_NONE
        self.shield_hits_left = 0
        self.shield_shrink_timer = 0.0
        self.speed_multiplier = 1.0      # ¡CORRECCIÓN! Reiniciamos la velocidad
        self.yellow_power_hits = 0
        self.orange_power_hits = 0
        self.red_power_hits = 0
        self.green_power_hits = 0
        self.has_extra_life = False      # ¡NUEVO! Reiniciamos la vida extra
        
        # Nuevas variables del reloj blanco
        self.white_zone_hits_left = 0
        self.white_activation_timer = 0.0
        
        # Variable del Reloj Amarillo (Vida Extra / Crucifijo)
        self.has_extra_life = False
        
    def grant_random_power(self, game):
        # Sorteamos entre los 4 poderes
        # Por defecto: Rojo 30%, Verde 30%, Amarillo 30%, Naranja 10%
        # Si Equal Powers está activo: 25% cada uno
        all_p = [
            (POWER_FIREBALL, RED, 25 if game.equal_powers_enabled else 30, game.remove_power_red),
            (POWER_SHIELD, GREEN, 25 if game.equal_powers_enabled else 30, game.remove_power_green),
            (POWER_SPEED, YELLOW, 25 if game.equal_powers_enabled else 30, game.remove_power_yellow),
            (POWER_ORANGE, ORANGE, 25 if game.equal_powers_enabled else 10, game.remove_power_orange),
            (POWER_MAGNET, GRAY, 25 if game.equal_powers_enabled else 15, not game.magnet_power_enabled)
        ]
        
        # Filtramos los que el usuario quitó
        available_powers = [p for p in all_p if not p[3]]
        
        if not available_powers:
            self.power_stored = POWER_NONE
            self.color = WHITE
            return

        total_weight = sum(p[2] for p in available_powers)
        r = random.random() * total_weight
        acc = 0
        for p_type, p_color, weight, removed in available_powers:
            acc += weight
            if r <= acc:
                self.power_stored = p_type
                self.color = p_color
                break

    def reroll_power(self, game):
        # El Reroll busca un poder diferente al actual
        all_p = [
            (POWER_FIREBALL, RED, 25 if game.equal_powers_enabled else 30, game.remove_power_red),
            (POWER_SHIELD, GREEN, 25 if game.equal_powers_enabled else 30, game.remove_power_green),
            (POWER_SPEED, YELLOW, 25 if game.equal_powers_enabled else 30, game.remove_power_yellow),
            (POWER_ORANGE, ORANGE, 25 if game.equal_powers_enabled else 10, game.remove_power_orange),
            (POWER_MAGNET, GRAY, 25 if game.equal_powers_enabled else 15, not game.magnet_power_enabled)
        ]
        # Filtramos el actual y los que el usuario quitó
        available_powers = [p for p in all_p if p[0] != self.power_stored and not p[3]]
        
        if not available_powers:
            # Si no hay más opciones, intentamos al menos dejar el actual si no está bloqueado
            if not any(p[0] == self.power_stored and not p[3] for p in all_p):
                self.power_stored = POWER_NONE
                self.color = WHITE
            return
            
        total_weight = sum(p[2] for p in available_powers)
        r = random.random() * total_weight
        acc = 0
        for p_type, p_color, weight, removed in available_powers:
            acc += weight
            if r <= acc:
                self.power_stored = p_type
                self.color = p_color
                break
    
    # Función que activa el poder guardado cuando presionamos 'D' o 'L'
    def activate_power(self):
        # Solo lo activamos si teníamos un poder guardado
        if self.power_stored != POWER_NONE:
            self.power_active = self.power_stored # El poder pasa de "guardado" a "activo"
            self.power_stored = POWER_NONE        # Vaciamos la reserva
            
            # Si el poder que activamos es el Escudo Gigante...
            if self.power_active == POWER_SHIELD:
                self.rect.height = PADDLE_HEIGHT * 2 # ¡La paleta se hace el doble de alta!
                self.shield_hits_left = 3            # Nos va a durar 3 golpes (balance)
                
                # Chequeamos que al crecer no se haya salido de la pantalla por abajo
                if self.rect.bottom > SCREEN_HEIGHT:
                    self.rect.bottom = SCREEN_HEIGHT
                    self.y_float = float(self.rect.y)
                    
            elif self.power_active == POWER_SPEED:
                self.speed_multiplier += 0.5 # Aumenta un 50% extra su velocidad
                self.color = WHITE # La paleta vuelve a ser blanca
                self.power_active = POWER_NONE # Se limpia porque ya aplicamos la mejora infinita
            
            # Si es la Bola de Fuego, no hacemos nada extra aquí. 
            # El color rojo ya lo tiene y el efecto ocurrirá cuando toque la pelota.
            
            elif self.power_active == POWER_MAGNET:
                self.magnet_hits_left = 3
                self.color = GRAY

    def move(self, direction, dt):
        self.y_float += direction * (PADDLE_SPEED * self.speed_multiplier) * dt
        self.rect.y = int(self.y_float)
        
        if self.rect.top < 0: 
            self.rect.top = 0 
            self.y_float = float(self.rect.y)
        if self.rect.bottom > SCREEN_HEIGHT: 
            self.rect.bottom = SCREEN_HEIGHT 
            self.y_float = float(self.rect.y)

    def draw(self, surface):
        # Ahora dibujamos la paleta usando su color dinámico
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Si tiene el poder IMAN activo, dibujamos las puntas de colores
        if self.power_active == POWER_MAGNET:
            # Punta Roja (Norte)
            pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y, self.rect.width, 10))
            # Punta Azul (Sur)
            pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.bottom - 10, self.rect.width, 10))

class Ball:
    def __init__(self, x, y):
        self.start_x = x 
        self.start_y = y
        self.rect = pygame.Rect(x - BALL_SIZE//2, y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = BALL_START_SPEED
        
        # ¡Nuevas variables de la pelota!
        self.color = WHITE
        self.is_fireball = False # Nos indica si la pelota está "prendida fuego"
        self.is_orange = False   # Nos indica si es la pelota tramposa (Espejismo)

    def reset_orange(self):
        if self.is_orange:
            self.rect.width = BALL_SIZE
            self.rect.height = BALL_SIZE
            self.speed /= 1.5
            self.is_orange = False
            self.color = WHITE

    def serve(self, direction_x):
        # Reiniciamos su tamaño por si acaso era Naranja gigante
        self.rect.width = BALL_SIZE
        self.rect.height = BALL_SIZE
        
        self.rect.center = (self.start_x, self.start_y)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.speed = BALL_START_SPEED 
        
        # Reiniciamos el estado de la pelota en cada saque
        self.color = WHITE
        self.is_fireball = False
        self.is_orange = False
        
        angle = random.uniform(-math.pi/4, math.pi/4) 
        self.vx = self.speed * math.cos(angle) * direction_x
        self.vy = self.speed * math.sin(angle)

    def update(self, dt, speed_multiplier=1.0):
        # Multiplicamos por speed_multiplier para hacer cámara lenta sin romper las físicas
        self.x_float += self.vx * speed_multiplier * dt
        self.y_float += self.vy * speed_multiplier * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def draw(self, surface):
        # Dibujamos la pelota con su color
        pygame.draw.rect(surface, self.color, self.rect)

class Game:
    def __init__(self):
        pygame.init() 
        pygame.mixer.init() # ¡NUEVO! Encendemos el sistema de sonido
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Kombat v0.3.1.1")
        
        self.clock = pygame.time.Clock() 
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.tiny_font = pygame.font.SysFont("Arial", 16, bold=False)
        
        self.paddle1 = Paddle(PADDLE_OFFSET, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.score1 = 0
        self.score2 = 0
        
        self.state = STATE_MAIN_MENU 
        self.serve_timer = 0    
        self.serve_direction = 1 
        self.winner_text = ""    
        
        # Botones del Menú Principal
        button_width = 300
        button_height = 80
        spacing = 40
        start_y = SCREEN_HEIGHT // 2
        
        self.btn_play_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height)
        self.btn_modifiers_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + button_height + spacing, button_width, button_height)
        
        # Panel de Modificadores (Más grande: 20 cm)
        panel_w = 700
        panel_h = 400
        self.modifiers_panel_rect = pygame.Rect(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        self.score_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 40, self.modifiers_panel_rect.y + 100, 80, 50)
        self.back_btn_rect = pygame.Rect(self.modifiers_panel_rect.right - 90, self.modifiers_panel_rect.y + 10, 80, 40)
        self.max_score = 6 
        
        # Scrollbar
        self.scroll_y = 0
        self.max_scroll = 150 # Comienza en 150 porque el menú está colapsado por defecto
        self.is_dragging_scrollbar = False
        self.scrollbar_rect = pygame.Rect(self.modifiers_panel_rect.right - 20, self.modifiers_panel_rect.y + 60, 10, self.modifiers_panel_rect.height - 70)
        self.scrollbar_thumb_height = 50
        self.scrollbar_thumb_rect = pygame.Rect(self.scrollbar_rect.x, self.scrollbar_rect.y, 10, self.scrollbar_thumb_height)
        self.scroll_offset_y = 0
        self.max_score = 6 
        self.ball_speed_multiplier_options = [1.01, 1.025, 1.05]
        self.ball_speed_multiplier_idx = 1 # Por defecto 1.025
        self.ball_speed_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 40, 0, 80, 50)
        
        # Variables de Modificadores
        self.match_point_enabled = False
        self.match_point_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, self.modifiers_panel_rect.y + 180, 30, 30) # Checkbox
        self.match_point_text_rect = pygame.Rect(0, 0, 0, 0)
        self.golden_goal_anim_enabled = True # Activado por defecto en el juego base
        self.golden_goal_anim_rect = pygame.Rect(0, 0, 30, 30)
        self.golden_goal_anim_text_rect = pygame.Rect(0, 0, 0, 0)
        self.show_golden_goal_anim = False
        self.golden_goal_anim_timer = 0
        self.experimental_golden_goal = False # Modo experimental en EXTRAS
        self.experimental_golden_goal_rect = pygame.Rect(0, 0, 30, 30)
        self.experimental_golden_goal_text_rect = pygame.Rect(0, 0, 0, 0)
        self.is_golden_goal_round = False # Indica si la ronda actual es decisiva
        
        # Sistema de Pestañas (Tabs) para Modificadores
        self.modifiers_tab = "ALL" # "ALL" o "EXTRAS"
        self.tab_all_rect = pygame.Rect(0, 0, 110, 45)
        self.tab_extras_rect = pygame.Rect(0, 0, 140, 45)
        
        self.reroll_enabled = True
        self.reroll_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, self.modifiers_panel_rect.y + 260, 30, 30) # Checkbox
        self.reroll_text_rect = pygame.Rect(0, 0, 0, 0) # Se actualizará al dibujar
        
        self.all_reroll_enabled = False
        self.all_reroll_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, self.modifiers_panel_rect.y + 310, 30, 30) # Checkbox
        self.all_reroll_text_rect = pygame.Rect(0, 0, 0, 0) # Se actualizará al dibujar
        
        self.equal_watches_enabled = False
        self.equal_watches_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, self.modifiers_panel_rect.y + 360, 30, 30) # Checkbox
        self.equal_watches_text_rect = pygame.Rect(0, 0, 0, 0) # Se actualizará al dibujar
        
        self.equal_powers_enabled = False
        self.equal_powers_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.equal_powers_text_rect = pygame.Rect(0, 0, 0, 0)
        
        # Animación de Match Point
        self.show_match_point_anim = False
        self.match_point_anim_timer = 0.0
        
        self.watches_kept_enabled = False
        self.watches_kept_rect = pygame.Rect(0, 0, 30, 30)
        self.watches_kept_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.equal_watches_enabled = False
        self.equal_watches_rect = pygame.Rect(0, 0, 30, 30)
        self.equal_watches_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.equal_powers_enabled = False
        self.equal_powers_rect = pygame.Rect(0, 0, 30, 30)
        self.equal_powers_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.remove_watches_expanded = False
        self.remove_watches_toggle_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_watches_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.remove_blue = False
        self.remove_blue_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_blue_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_red = False
        self.remove_red_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_red_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_purple = False
        self.remove_purple_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_purple_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_white = False
        self.remove_white_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_white_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_yellow = False
        self.remove_yellow_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_yellow_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.remove_power_expanded = False
        self.remove_power_toggle_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_power_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_power_red = False
        self.remove_power_red_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_power_red_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_power_green = False
        self.remove_power_green_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_power_green_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_power_yellow = False
        self.remove_power_yellow_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_power_yellow_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_power_orange = False
        self.remove_power_orange_rect = pygame.Rect(0, 0, 30, 30)
        self.remove_power_orange_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.experimental_expanded = False
        self.experimental_toggle_rect = pygame.Rect(0, 0, 30, 30)
        self.experimental_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        self.orange_watch_enabled = False
        self.orange_watch_rect = pygame.Rect(0, 0, 30, 30)
        self.orange_watch_text_rect = pygame.Rect(0, 0, 0, 0)
        self.magnet_power_enabled = False
        self.magnet_power_rect = pygame.Rect(0, 0, 30, 30)
        self.magnet_power_text_rect = pygame.Rect(0, 0, 0, 0)
        
        self.p1_zone_type = 0
        self.p2_zone_type = 0
        
        # Modificador 1: Aparición de Relojes en el centro
        self.watch_spawn_hits_options = [3, 5, 10, 15]
        self.watch_spawn_hits_idx = 2 # 10 hits (Predeterminado)
        self.watch_spawn_hits_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 80, 40)
        self.watch_spawn_hits_text_rect = pygame.Rect(0, 0, 0, 0)
        
        # Modificador 2: Obtención automática de Poderes
        self.power_auto_grant_hits_options = [3, 5, 7, 10, 12]
        self.power_auto_grant_hits_idx = 2 # 7 hits (Predeterminado)
        self.power_auto_grant_hits_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 80, 40)
        self.power_auto_grant_hits_text_rect = pygame.Rect(0, 0, 0, 0)
        self.global_power_hits = 0 # Contador separado para los poderes
        
        # Modificador 3: Empezar con un poder
        self.start_with_power_enabled = True
        self.start_with_power_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.start_with_power_text_rect = pygame.Rect(0, 0, 0, 0)
        
        # Modificadores para eliminar poderes de paleta
        self.remove_power_expanded = False
        self.remove_power_toggle_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_power_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_power_red = False
        self.remove_power_red_rect = pygame.Rect(0,0,0,0)
        self.remove_power_red_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_green = False
        self.remove_power_green_rect = pygame.Rect(0,0,0,0)
        self.remove_power_green_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_yellow = False
        self.remove_power_yellow_rect = pygame.Rect(0,0,0,0)
        self.remove_power_yellow_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_orange = False
        self.remove_power_orange_rect = pygame.Rect(0,0,0,0)
        self.remove_power_orange_text_rect = pygame.Rect(0,0,0,0)

        # Contenido Experimental
        self.experimental_expanded = False
        self.experimental_toggle_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.experimental_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        self.orange_watch_enabled = False
        self.orange_watch_rect = pygame.Rect(0, 0, 0, 0)
        self.orange_watch_text_rect = pygame.Rect(0, 0, 0, 0)

        self.remove_watches_expanded = False
        self.remove_watches_toggle_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_watches_toggle_text_rect = pygame.Rect(0, 0, 0, 0)
        
        # Botones para remover relojes
        self.remove_blue = False
        self.remove_red = False
        self.remove_purple = False
        self.remove_white = False
        self.remove_yellow = False
        
        self.remove_blue_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_red_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_purple_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_white_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        self.remove_yellow_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 0, 30, 30)
        
        self.remove_blue_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_red_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_purple_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_white_text_rect = pygame.Rect(0, 0, 0, 0)
        self.remove_yellow_text_rect = pygame.Rect(0, 0, 0, 0)
        
        # Botones de Game Over
        self.btn_gameover_restart = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 300, 60)
        self.btn_gameover_menu = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, 300, 60)
        
        # ¡NUEVO! Variables para el Reloj de Arena
        self.global_hits = 0        # Toques totales en la ronda
        self.hourglass_rect = None  # Si hay un reloj, guardamos su posición aquí
        self.hourglass_type = 0     # 1 = Reloj Azul, 2 = Reloj Rojo, 3 = Violeta, 4 = Blanco, 5 = Amarillo
        self.zone_type = 0          # 1 = Zona Azul (Lenta), 2 = Zona Roja (Rápida), 3 = Violeta, 4 = Blanco
        self.slow_zone_owner = 0    # 0 = Nadie, 1 = Zona Izquierda, 2 = Zona Derecha
        self.last_hitter = 0        # 1 o 2, dependiendo quién golpeó último
        
        # Cargamos los archivos de sonido desde la nueva carpeta "sounds"
        self.hit_sound = pygame.mixer.Sound(os.path.join("sounds", "hit.wav"))
        self.pop_sound = pygame.mixer.Sound(os.path.join("sounds", "pop.wav"))
        
        self.item_sound = pygame.mixer.Sound(os.path.join("sounds", "item_get.wav")) # Sonido Turututuu
        self.item_sound.set_volume(0.5) # Le bajamos el volumen a la mitad para que no aturda
        
        self.error_sound = pygame.mixer.Sound(os.path.join("sounds", "error.wav")) # Sonido de Acceso Denegado
        self.error_sound.set_volume(0.5)
        
        self.fire_sound = pygame.mixer.Sound(os.path.join("sounds", "fire.wav"))
        self.fire_sound.set_volume(0.5) # Le bajamos el volumen a la mitad (50%)
        
        self.uuui_sound = pygame.mixer.Sound(os.path.join("sounds", "uuui.wav"))
        self.uuui_sound.set_volume(0.8) # Buen volumen para indicar el zoom
        
        self.bell_sound = pygame.mixer.Sound(os.path.join("sounds", "campana.wav"))
        self.bell_sound.set_volume(0.6) # Volumen campana violeta
        
        self.divine_sound = pygame.mixer.Sound(os.path.join("sounds", "divino.wav"))
        self.divine_sound.set_volume(0.8) # Volumen del reloj blanco
        
        self.life_sound = pygame.mixer.Sound(os.path.join("sounds", "vida.wav"))
        self.life_sound.set_volume(0.8) # Volumen de la vida extra

        self.match_point_sound = pygame.mixer.Sound(os.path.join("sounds", "match_point_bell.wav"))
        self.match_point_sound.set_volume(0.8)
        
        self.golden_goal_sound = pygame.mixer.Sound(os.path.join("sounds", "golden_goal.wav"))
        self.golden_goal_sound.set_volume(0.9) # ¡JACKPOT!
        
        self.wall_sound_cooldown = 0.0 # Cooldown para evitar el bug del ruido múltiple

    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        
        # Reiniciamos las variables de la zona temporal
        self.global_hits = 0
        self.hourglass_rect = None
        self.hourglass_type = 0
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.last_hitter = 0
        
        # Volvemos a centrar las paletas y usamos nuestra nueva función reset() para borrar poderes
        self.paddle1.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle1.y_float = float(self.paddle1.rect.y)
        self.paddle1.reset()
        
        self.paddle2.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle2.y_float = float(self.paddle2.rect.y)
        self.paddle2.reset()

        # ¡KOMBAT INICIA AHORA! Solo si el modificador está activo
        if self.start_with_power_enabled:
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
        
        self.state = STATE_SERVE 
        self.serve_timer = 1.0 
        self.serve_direction = random.choice([1, -1]) 
        self.ball.serve(self.serve_direction)

    def handle_input(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Click izquierdo
                    if self.state == STATE_MAIN_MENU:
                        if self.btn_play_rect.collidepoint(event.pos):
                            self.hit_sound.play()
                            self.state = STATE_PRESS_TO_START
                        elif self.btn_modifiers_rect.collidepoint(event.pos):
                            self.hit_sound.play()
                            self.state = STATE_MODIFIERS
                    elif self.state == STATE_MODIFIERS:
                        if self.scrollbar_thumb_rect.collidepoint(event.pos):
                            self.is_dragging_scrollbar = True
                            self.scroll_offset_y = event.pos[1] - self.scrollbar_thumb_rect.y
                        elif self.back_btn_rect.collidepoint(event.pos):
                            self.hit_sound.play()
                            self.state = STATE_MAIN_MENU
                            self.scroll_y = 0
                            self.scrollbar_thumb_rect.y = self.scrollbar_rect.y
                            self.remove_watches_expanded = False
                        
                        # --- CLICS EN PESTAÑAS (TABS) ---
                        elif self.tab_all_rect.collidepoint(event.pos):
                            if self.modifiers_tab != "ALL":
                                self.pop_sound.play()
                                self.modifiers_tab = "ALL"
                                self.scroll_y = 0
                        elif self.tab_extras_rect.collidepoint(event.pos):
                            if self.modifiers_tab != "EXTRAS":
                                self.pop_sound.play()
                                self.modifiers_tab = "EXTRAS"
                                self.scroll_y = 0
                                
                        # --- CLICS EN EL CONTENIDO DEL PANEL ---
                        elif self.modifiers_panel_rect.collidepoint(event.pos):
                            # Solo procesamos si el click es en la zona de opciones (debajo del título)
                            if event.pos[1] > self.modifiers_panel_rect.top + 60:
                                if self.modifiers_tab == "ALL":
                                    # --- LÓGICA PARA PESTAÑA ALL ---
                                    if self.score_btn_rect.collidepoint(event.pos):
                                        self.pop_sound.play()
                                        if self.max_score == 3: self.max_score = 6
                                        elif self.max_score == 6: self.max_score = 9
                                        else: self.max_score = 3
                                    elif self.ball_speed_btn_rect.collidepoint(event.pos):
                                        self.pop_sound.play()
                                        self.ball_speed_multiplier_idx = (self.ball_speed_multiplier_idx + 1) % len(self.ball_speed_multiplier_options)
                                    elif self.match_point_rect.collidepoint(event.pos) or self.match_point_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.match_point_enabled = not self.match_point_enabled
                                    elif self.golden_goal_anim_rect.collidepoint(event.pos) or self.golden_goal_anim_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.golden_goal_anim_enabled = not self.golden_goal_anim_enabled
                                    elif self.reroll_rect.collidepoint(event.pos) or self.reroll_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.reroll_enabled = not self.reroll_enabled
                                    elif self.reroll_enabled and (self.all_reroll_rect.collidepoint(event.pos) or self.all_reroll_text_rect.collidepoint(event.pos)):
                                        self.pop_sound.play(); self.all_reroll_enabled = not self.all_reroll_enabled
                                    elif self.equal_watches_rect.collidepoint(event.pos) or self.equal_watches_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.equal_watches_enabled = not self.equal_watches_enabled
                                    elif self.equal_powers_rect.collidepoint(event.pos) or self.equal_powers_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.equal_powers_enabled = not self.equal_powers_enabled
                                    elif self.watches_kept_rect.collidepoint(event.pos) or self.watches_kept_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.watches_kept_enabled = not self.watches_kept_enabled
                                    elif self.watch_spawn_hits_rect.collidepoint(event.pos) or self.watch_spawn_hits_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play()
                                        self.watch_spawn_hits_idx = (self.watch_spawn_hits_idx + 1) % len(self.watch_spawn_hits_options)
                                    elif self.power_auto_grant_hits_rect.collidepoint(event.pos) or self.power_auto_grant_hits_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play()
                                        self.power_auto_grant_hits_idx = (self.power_auto_grant_hits_idx + 1) % len(self.power_auto_grant_hits_options)
                                    elif self.start_with_power_rect.collidepoint(event.pos) or self.start_with_power_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.start_with_power_enabled = not self.start_with_power_enabled
                                    elif self.remove_watches_toggle_rect.collidepoint(event.pos) or self.remove_watches_toggle_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.remove_watches_expanded = not self.remove_watches_expanded
                                    elif self.remove_power_toggle_rect.collidepoint(event.pos) or self.remove_power_toggle_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.remove_power_expanded = not self.remove_power_expanded
                                    elif self.experimental_toggle_rect.collidepoint(event.pos) or self.experimental_toggle_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.experimental_expanded = not self.experimental_expanded
                                    
                                    # Hijos de acordeones (solo si están expandidos)
                                    if self.remove_watches_expanded:
                                        if self.remove_blue_rect.collidepoint(event.pos) or self.remove_blue_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_blue = not self.remove_blue
                                        elif self.remove_red_rect.collidepoint(event.pos) or self.remove_red_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_red = not self.remove_red
                                        elif self.remove_purple_rect.collidepoint(event.pos) or self.remove_purple_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_purple = not self.remove_purple
                                        elif self.remove_white_rect.collidepoint(event.pos) or self.remove_white_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_white = not self.remove_white
                                        elif self.remove_yellow_rect.collidepoint(event.pos) or self.remove_yellow_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_yellow = not self.remove_yellow
                                            
                                    if self.remove_power_expanded:
                                        if self.remove_power_red_rect.collidepoint(event.pos) or self.remove_power_red_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_power_red = not self.remove_power_red
                                        elif self.remove_power_green_rect.collidepoint(event.pos) or self.remove_power_green_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_power_green = not self.remove_power_green
                                        elif self.remove_power_yellow_rect.collidepoint(event.pos) or self.remove_power_yellow_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_power_yellow = not self.remove_power_yellow
                                        elif self.remove_power_orange_rect.collidepoint(event.pos) or self.remove_power_orange_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.remove_power_orange = not self.remove_power_orange
                                            
                                    if self.experimental_expanded:
                                        if self.orange_watch_rect.collidepoint(event.pos) or self.orange_watch_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.orange_watch_enabled = not self.orange_watch_enabled
                                        elif self.magnet_power_rect.collidepoint(event.pos) or self.magnet_power_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.magnet_power_enabled = not self.magnet_power_enabled
                                        elif self.experimental_golden_goal_rect.collidepoint(event.pos) or self.experimental_golden_goal_text_rect.collidepoint(event.pos):
                                            self.pop_sound.play(); self.experimental_golden_goal = not self.experimental_golden_goal
                                            
                                elif self.modifiers_tab == "EXTRAS":
                                    # --- LÓGICA PARA PESTAÑA EXTRAS (Acceso Directo) ---
                                    if self.orange_watch_rect.collidepoint(event.pos) or self.orange_watch_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.orange_watch_enabled = not self.orange_watch_enabled
                                    elif self.magnet_power_rect.collidepoint(event.pos) or self.magnet_power_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.magnet_power_enabled = not self.magnet_power_enabled
                                    elif self.experimental_golden_goal_rect.collidepoint(event.pos) or self.experimental_golden_goal_text_rect.collidepoint(event.pos):
                                        self.pop_sound.play(); self.experimental_golden_goal = not self.experimental_golden_goal
                    elif self.state == STATE_GAME_OVER:
                        if self.btn_gameover_restart.collidepoint(event.pos):
                            self.hit_sound.play()
                            self.reset_game()
                        elif self.btn_gameover_menu.collidepoint(event.pos):
                            self.hit_sound.play()
                            self.state = STATE_MAIN_MENU
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_scrollbar = False
                    
            if event.type == pygame.MOUSEMOTION:
                if getattr(self, 'state', None) == STATE_MODIFIERS and getattr(self, 'is_dragging_scrollbar', False):
                    new_y = event.pos[1] - self.scroll_offset_y
                    new_y = max(self.scrollbar_rect.top, min(new_y, self.scrollbar_rect.bottom - self.scrollbar_thumb_height))
                    self.scrollbar_thumb_rect.y = new_y
                    
                    # Update scroll_y
                    scroll_fraction = (self.scrollbar_thumb_rect.y - self.scrollbar_rect.top) / (self.scrollbar_rect.height - self.scrollbar_thumb_height)
                    self.scroll_y = scroll_fraction * self.max_scroll
            
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_PRESS_TO_START:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                
                # ¡NUEVO! Detección de las teclas D y L para activar poderes
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_d:
                        self.paddle1.activate_power()
                    if event.key == pygame.K_RIGHT:
                        self.paddle2.activate_power()

        keys = pygame.key.get_pressed()
        
        if self.state in [STATE_PLAYING, STATE_SERVE]:
            if keys[pygame.K_w]:
                self.paddle1.move(-1, dt) 
            if keys[pygame.K_s]:
                self.paddle1.move(1, dt)  
            
            if keys[pygame.K_UP]:
                self.paddle2.move(-1, dt)
            if keys[pygame.K_DOWN]:
                self.paddle2.move(1, dt)

    def check_collisions(self):
        # Colisiones con Techo y Piso
        if self.ball.rect.top <= 0:
            self.ball.rect.top = 0
            self.ball.y_float = float(self.ball.rect.y)
            self.ball.vy = abs(self.ball.vy) 
            if self.wall_sound_cooldown <= 0:
                self.hit_sound.play() # Sonido al chocar el techo
                self.wall_sound_cooldown = 0.25 # Reiniciamos el cooldown
        elif self.ball.rect.bottom >= SCREEN_HEIGHT:
            self.ball.rect.bottom = SCREEN_HEIGHT
            self.ball.y_float = float(self.ball.rect.y)
            self.ball.vy = -abs(self.ball.vy) 
            if self.wall_sound_cooldown <= 0:
                self.hit_sound.play() # Sonido al chocar el piso
                self.wall_sound_cooldown = 0.25 # Reiniciamos el cooldown

        # Colisión con el Reloj de Arena (Si existe)
        if self.hourglass_rect and self.ball.rect.colliderect(self.hourglass_rect):
            if self.hourglass_type == 1:
                self.item_sound.play() # Suena la fanfarria de victoria
            elif self.hourglass_type == 2:
                self.error_sound.play() # Suena el error grave
            elif self.hourglass_type == 3:
                self.bell_sound.play() # Campana misteriosa violeta
            elif self.hourglass_type == 4:
                self.divine_sound.play() # Sonido angelical blanco
            elif self.hourglass_type == 5:
                self.life_sound.play() # Sonido celestial amarillo (Crucifijo)
                
            if self.hourglass_type == 5:
                # El reloj amarillo otorga una vida extra, no es una zona
                self.global_hits = 0 # Reseteamos toques globales al capturar
                if self.last_hitter == 1:
                    self.paddle1.has_extra_life = True
                elif self.last_hitter == 2:
                    self.paddle2.has_extra_life = True
                self.hourglass_rect = None
            else:
                h_type = self.hourglass_type
                self.hourglass_rect = None # Desaparece el reloj
                self.global_hits = 0 # Reseteamos toques globales al capturar
                if self.last_hitter != 0:
                    if self.watches_kept_enabled:
                        if self.last_hitter == 1:
                            self.p1_zone_type = h_type
                        else:
                            self.p2_zone_type = h_type
                    else:
                        self.zone_type = h_type # Copiamos el tipo de reloj a la zona
                        self.slow_zone_owner = self.last_hitter # Activamos la zona
                    
                    # ¡Si agarró el reloj violeta, sus toques actuales se resetean!
                    if h_type == 3:
                        if self.last_hitter == 1:
                            self.paddle1.hits = 0
                        elif self.last_hitter == 2:
                            self.paddle2.hits = 0
                            
                    # ¡Si agarró el reloj blanco, activamos el timer, reseteamos sus toques y borramos cualquier poder!
                    if self.hourglass_type == 4:
                        if self.last_hitter == 1:
                            self.paddle1.reset()
                            self.paddle1.white_activation_timer = 0.05
                        elif self.last_hitter == 2:
                            self.paddle2.reset()
                            self.paddle2.white_activation_timer = 0.05
                    
                    # --- ¡RELOJ NARANJA! (Trampa Instantánea) ---
                    if self.hourglass_type == 6:
                        self.uuui_sound.play()
                        self.ball.is_orange = True
                        self.ball.color = ORANGE
                        self.ball.rect.width = BALL_SIZE * 2
                        self.ball.rect.height = BALL_SIZE * 2
                        self.ball.speed *= 1.5
                        self.hourglass_rect = None # Desaparece
                        self.global_hits = 0 # Reiniciamos el timer
                        return # Salimos porque ya se procesó

        # Colisiones de Gol / Rebote Naranja / Barrera Amarilla
        if self.ball.rect.right < 0: 
            if self.ball.is_orange:
                # Primero restauramos su tamaño normal
                self.ball.rect.width = BALL_SIZE
                self.ball.rect.height = BALL_SIZE
                # Luego la colocamos justo pegada al borde izquierdo
                self.ball.rect.left = 0
                self.ball.x_float = float(self.ball.rect.x)
        

                self.ball.vx *= -1
                self.ball.speed /= 1.5 # Le quitamos el buff de velocidad
                self.ball.is_orange = False
                self.ball.color = WHITE
                self.hit_sound.play() # Sonido de rebote contra la pared virtual
            elif self.paddle1.has_extra_life:
                # ¡La barrera amarilla (Crucifijo) nos salva del gol!
                self.ball.rect.left = 0
                self.ball.x_float = float(self.ball.rect.x)
        

                self.ball.vx *= -1
                self.paddle1.has_extra_life = False # Perdemos la vida extra
                self.hit_sound.play() # Sonido de rebote
            else:
                self.goal_scored(2) # Anota el Jugador 2
        elif self.ball.rect.left > SCREEN_WIDTH: 
            if self.ball.is_orange:
                # Primero restauramos su tamaño normal
                self.ball.rect.width = BALL_SIZE
                self.ball.rect.height = BALL_SIZE
                # Luego la colocamos justo pegada al borde derecho
                self.ball.rect.right = SCREEN_WIDTH
                self.ball.x_float = float(self.ball.rect.x)
        

                self.ball.vx *= -1
                self.ball.speed /= 1.5 # Le quitamos el buff de velocidad
                self.ball.is_orange = False
                self.ball.color = WHITE
                self.hit_sound.play() # Sonido de rebote contra la pared virtual
            elif self.paddle2.has_extra_life:
                # ¡La barrera amarilla (Crucifijo) nos salva del gol!
                self.ball.rect.right = SCREEN_WIDTH
                self.ball.x_float = float(self.ball.rect.x)
        

                self.ball.vx *= -1
                self.paddle2.has_extra_life = False # Perdemos la vida extra
                self.hit_sound.play() # Sonido de rebote
            else:
                self.goal_scored(1) # Anota el Jugador 1

        # Colisiones con las Paletas
        if self.ball.vx < 0 and self.ball.rect.colliderect(self.paddle1.rect):
            self.handle_paddle_collision(self.paddle1, 1) 
        elif self.ball.vx > 0 and self.ball.rect.colliderect(self.paddle2.rect):
            self.handle_paddle_collision(self.paddle2, -1) 

    def handle_paddle_collision(self, paddle, direction_x):
        # Si la pelota era naranja y alguien le pegó... ¡Pierde el punto!
        if self.ball.is_orange:
            self.ball.reset_orange() # Restauramos físicamente antes de procesar el punto
            self.pop_sound.play()
            if paddle == self.paddle1:
                self.goal_scored(2) # Anota el Jugador 2
                return
            else:
                self.goal_scored(1) # Anota el Jugador 1
                return
            return # Cortamos la colisión acá porque ya fue punto
            
        # ¡NUEVO! Reproducimos el sonido de burbuja (POP) al tocar la paleta
        self.pop_sound.play() 
        
        # Guardamos quién le pegó
        self.last_hitter = 1 if paddle == self.paddle1 else 2
        
        # 1. Si la pelota viene como Bola de Fuego (y acaba de chocar mi paleta), se apaga.
        if self.ball.is_fireball:
            self.ball.is_fireball = False
            self.ball.color = WHITE
            self.ball.speed /= 2 # Le quitamos la velocidad x2
            self.fire_sound.fadeout(500) # Hacemos que el sonido se desvanezca más rápido (0.5 seg)

        # 2. Aumento de dificultad estándar del Pong Clásico
        self.ball.speed *= self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]
        
        # 3. ¡Sumamos un golpe a la paleta!
        # EXCEPCIONES: No suma si tiene Muro Blanco o si tiene Escudo (Poder Verde) activo
        is_p1_white = (paddle == self.paddle1 and (self.p1_zone_type == 4 or (self.slow_zone_owner == 1 and self.zone_type == 4)))
        is_p2_white = (paddle == self.paddle2 and (self.p2_zone_type == 4 or (self.slow_zone_owner == 2 and self.zone_type == 4)))
        
        if is_p1_white or is_p2_white or paddle.power_active == POWER_SHIELD:
            pass # No suma puntos para evitar bucles o errores
        else:
            paddle.hits += 1
            
        # ¿Cuántos golpes necesita la paleta? Normalmente 7, pero si tiene zona violeta, solo 3
        # ¿Cuántos golpes necesita la paleta? Usamos el valor del modificador
        required_hits = self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]
        if self.zone_type == 3:
            if paddle == self.paddle1 and self.slow_zone_owner == 1:
                required_hits = 3
            elif paddle == self.paddle2 and self.slow_zone_owner == 2:
                required_hits = 3
                
        # ¿Llegó a la cantidad necesaria?
        if paddle.hits >= required_hits:
            paddle.grant_random_power(self)
            paddle.hits = 0

        # 4. Revisamos si la paleta tenía un poder ACTIVO listo para reaccionar al golpe
        if paddle.power_active == POWER_FIREBALL:
            paddle.power_active = POWER_NONE # Se gastó el poder
            paddle.color = WHITE             # Paleta vuelve a la normalidad
            self.ball.is_fireball = True     # ¡Bola se enciende!
            self.ball.color = RED
            self.ball.speed *= 2             # ¡Súper velocidad!
            self.fire_sound.play(-1)         # Reproduce el fuego en bucle infinito (-1)
            
        elif paddle.power_active == POWER_ORANGE:
            paddle.power_active = POWER_NONE
            paddle.color = WHITE
            self.ball.is_orange = True
            self.ball.color = ORANGE
            
            # ¡Hacemos la pelota del doble de tamaño y un 50% más rápida!
            self.ball.rect.width = BALL_SIZE * 2
            self.ball.rect.height = BALL_SIZE * 2
            self.ball.rect.x -= BALL_SIZE // 2
            self.ball.rect.y -= BALL_SIZE // 2
            self.ball.speed *= 1.5 # Buff extra de velocidad
            
            self.uuui_sound.play()           # Sonido de caricatura "Uuui"
            
        elif paddle.power_active == POWER_SHIELD:
            paddle.shield_hits_left -= 1     # Gastamos 1 golpe del escudo gigante
            if paddle.shield_hits_left <= 0: # Si ya se acabaron los golpes...
                paddle.shield_shrink_timer = 0.1 # Iniciamos el cooldown de 0.1s
                
        elif paddle.power_active == POWER_MAGNET:
            paddle.magnet_hits_left -= 1
            if paddle.magnet_hits_left <= 0:
                paddle.power_active = POWER_NONE
                paddle.color = WHITE

        # Rerolls de Poderes (Amarillo y Naranja)
        if self.reroll_enabled:
            if paddle.power_stored == POWER_SPEED:
                paddle.yellow_power_hits += 1
                if paddle.yellow_power_hits >= 2:
                    paddle.reroll_power(self)
                    paddle.yellow_power_hits = 0
                    
            elif paddle.power_stored == POWER_ORANGE:
                paddle.orange_power_hits += 1
                if paddle.orange_power_hits >= 2:
                    paddle.reroll_power(self)
                    paddle.orange_power_hits = 0
            
            # Rerolls para Rojo y Verde si All Reroll está activado
            if self.all_reroll_enabled:
                if paddle.power_stored == POWER_FIREBALL:
                    paddle.red_power_hits += 1
                    if paddle.red_power_hits >= 2:
                        paddle.reroll_power(self)
                        paddle.red_power_hits = 0
                elif paddle.power_stored == POWER_SHIELD:
                    paddle.green_power_hits += 1
                    if paddle.green_power_hits >= 2:
                        paddle.reroll_power(self)
                        paddle.green_power_hits = 0
        
        # 5. Matemáticas de rebote
        relative_intersect_y = (paddle.rect.y + (paddle.rect.height / 2)) - self.ball.rect.centery
        normalized_relative_intersection_y = (relative_intersect_y / (paddle.rect.height / 2))
        bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE * -1
        
        self.ball.vx = self.ball.speed * math.cos(bounce_angle) * direction_x
        self.ball.vy = self.ball.speed * math.sin(bounce_angle)
        
        if direction_x == 1:
            self.ball.rect.left = paddle.rect.right
        else:
            self.ball.rect.right = paddle.rect.left
        self.ball.x_float = float(self.ball.rect.x)
        

        
        # --- ¡CORRECCIÓN! Lógica de expiración del Muro Blanco ---
        if self.watches_kept_enabled:
            if paddle == self.paddle1 and self.p1_zone_type == 4:
                self.paddle1.white_zone_hits_left -= 1
                if self.paddle1.white_zone_hits_left <= 0:
                    self.paddle1.reset()
                    self.p1_zone_type = 0
            elif paddle == self.paddle2 and self.p2_zone_type == 4:
                self.paddle2.white_zone_hits_left -= 1
                if self.paddle2.white_zone_hits_left <= 0:
                    self.paddle2.reset()
                    self.p2_zone_type = 0
        else:
            if self.zone_type == 4:
                if paddle == self.paddle1 and self.slow_zone_owner == 1:
                    self.paddle1.white_zone_hits_left -= 1
                    if self.paddle1.white_zone_hits_left <= 0:
                        self.paddle1.reset()
                        self.zone_type = 0
                        self.slow_zone_owner = 0
                elif paddle == self.paddle2 and self.slow_zone_owner == 2:
                    self.paddle2.white_zone_hits_left -= 1
                    if self.paddle2.white_zone_hits_left <= 0:
                        self.paddle2.reset()
                        self.zone_type = 0
                        self.slow_zone_owner = 0

        # 1. Relojes físicos en el centro
        # SOLO si NO hay un muro blanco activo en ninguna parte
        is_any_white = (self.zone_type == 4 or self.p1_zone_type == 4 or self.p2_zone_type == 4)
        if not is_any_white:
            self.global_hits += 1
            if self.global_hits >= self.watch_spawn_hits_options[self.watch_spawn_hits_idx]:
                self.global_hits = 0
                self.spawn_random_watch()

    def spawn_random_watch(self):
        # Calculamos relojes disponibles
        available_watches = []
        if not self.remove_blue: available_watches.append((1, 25))
        if not self.remove_red: available_watches.append((2, 20))
        if not self.remove_purple: available_watches.append((3, 20))
        if not self.remove_white: available_watches.append((4, 10))
        if not self.remove_yellow: available_watches.append((5, 25))
        if self.orange_watch_enabled: available_watches.append((6, 20)) # Reloj Naranja (Opcional)
        
        # SEGURIDAD: Si no hay NINGÚN reloj habilitado, habilitamos el azul por defecto para evitar crash
        if not available_watches:
            available_watches.append((1, 100))
        
        if available_watches:
            if self.hourglass_rect is None:
                self.hourglass_rect = pygame.Rect(SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 - 20, 30, 40)
            
            # Sorteamos el nuevo tipo (evitando que sea el mismo si es re-roll)
            old_type = self.hourglass_type
            while True:
                if self.equal_watches_enabled:
                    new_type = random.choice([w[0] for w in available_watches])
                else:
                    total_weight = sum([w[1] for w in available_watches])
                    r_clock = random.random() * total_weight
                    acum = 0
                    for w, weight in available_watches:
                        acum += weight
                        if r_clock <= acum:
                            new_type = w
                            break
                if len(available_watches) <= 1 or new_type != old_type:
                    self.hourglass_type = new_type
                    break

    def goal_scored(self, player):
        # Apagamos el fuego de a poco si alguien hace gol
        self.fire_sound.fadeout(500)
        
        # 1. ¿Era esta una ronda de GOLDEN GOAL (Muerte Súbita)?
        if self.is_golden_goal_round:
            self.is_golden_goal_round = False # Consumimos el efecto
            if player == 1:
                self.score1 = self.max_score
                self.winner_text = "¡Jugador 1 Gana!\n(por regla GOLDEN GOAL)"
            else:
                self.score2 = self.max_score
                self.winner_text = "¡Jugador 2 Gana!\n(por regla GOLDEN GOAL)"
            self.state = STATE_GAME_OVER
            return # Terminamos aquí

        # 2. Reiniciamos las mecánicas globales para el próximo saque
        self.global_hits = 0
        self.hourglass_rect = None
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.p1_zone_type = 0
        self.p2_zone_type = 0
        self.last_hitter = 0
        
        # Reiniciamos paletas
        self.paddle1.reset()
        self.paddle2.reset()
        
        # Si el modificador está activo, otorgamos poderes al empezar
        if self.start_with_power_enabled:
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
        
        # 3. Lógica normal de anotación
        if player == 1:
            self.score1 += 1
            serve_direction = 1 # El Jugador 2 recibe el saque
        else:
            self.score2 += 1
            serve_direction = -1 # El Jugador 1 recibe el saque

        # 4. Comprobamos victoria o continuación
        if (self.score1 >= self.max_score or self.score2 >= self.max_score):
            if not self.match_point_enabled:
                self.state = STATE_GAME_OVER
                self.winner_text = f"¡Jugador {1 if self.score1 >= self.max_score else 2} Gana la Partida!"
            else:
                # Lógica de Match Point (Diferencia de 2)
                if abs(self.score1 - self.score2) >= 2:
                    self.state = STATE_GAME_OVER
                    winner = 1 if self.score1 >= self.max_score else 2
                    self.winner_text = f"¡Jugador {winner} Gana!\n(por diferencia de puntos)"
                else:
                    self.state = STATE_SERVE
                    self.serve_direction = serve_direction
                    self.ball.serve(self.serve_direction)
        else:
            self.state = STATE_SERVE
            self.serve_direction = serve_direction
            self.ball.serve(self.serve_direction)
            
            # --- NUEVO! Probabilidad de que la PRÓXIMA ronda sea Golden Goal ---
            if self.experimental_golden_goal:
                if random.random() < 0.15: # 15% de probabilidad
                    self.is_golden_goal_round = True
        
        # --- ¡CORRECCIÓN FINAL! Detección de Animación de Match Point ---
        # Si el juego va a continuar (estamos en STATE_SERVE), calculamos si es Match Point
        # EXCLUSIVO: Solo si el modificador está activo
        if self.state == STATE_SERVE:
            if self.match_point_enabled:
                pts_to_win1 = max(self.max_score, self.score2 + 2) - self.score1
                pts_to_win2 = max(self.max_score, self.score1 + 2) - self.score2
                
                if pts_to_win1 == 1 or pts_to_win2 == 1:
                    self.show_match_point_anim = True
                    self.match_point_anim_timer = 2.1
                    self.serve_timer = 2.5
                    self.match_point_sound.play() # ¡TING-TING-TING!
                else:
                    self.show_match_point_anim = False
                    self.serve_timer = 1.0
            else:
                # Partida normal: Sin animación de Match Point
                self.show_match_point_anim = False
                self.serve_timer = 1.0
                
        # --- NUEVO! Detección de Golden Goal (Estético por defecto) ---
        if self.state == STATE_SERVE and self.golden_goal_anim_enabled:
            # Si ambos están a 1 punto de ganar y NO está el modo Match Point (que requiere diferencia de 2)
            if not self.match_point_enabled:
                if self.score1 == self.max_score - 1 and self.score2 == self.max_score - 1:
                    self.show_golden_goal_anim = True
                    self.golden_goal_anim_timer = 2.1
                    self.serve_timer = 2.5
                    self.golden_goal_sound.play() # ¡JACKPOT!
            else:
                # Si Match Point está activo, Golden Goal estético no tiene sentido porque el juego no termina en el sig punto
                self.show_golden_goal_anim = False
        
        # --- NUEVO! Lógica de Golden Goal Experimental (Ronda al azar) ---
        if self.state == STATE_SERVE and self.experimental_golden_goal and not self.show_golden_goal_anim:
            # Si se marcó la ronda como Golden Goal en goal_scored, activamos la animación
            if self.is_golden_goal_round:
                self.show_golden_goal_anim = True
                self.golden_goal_anim_timer = 2.1
                self.serve_timer = 2.5 # Damos tiempo para la animación
                self.golden_goal_sound.play()
                
    def update(self, dt):
        if self.state == STATE_SERVE:
            self.serve_timer -= dt 
            if self.serve_timer <= 0: 
                self.state = STATE_PLAYING 
            
            # Actualizamos el timer de la animación de Match Point
            if self.show_match_point_anim and self.match_point_anim_timer > 0:
                self.match_point_anim_timer -= dt
                if self.match_point_anim_timer <= 0:
                    self.show_match_point_anim = False
            
            # Actualizamos el timer de Golden Goal
            if self.show_golden_goal_anim and self.golden_goal_anim_timer > 0:
                self.golden_goal_anim_timer -= dt
                if self.golden_goal_anim_timer <= 0:
                    self.show_golden_goal_anim = False
                
        elif self.state == STATE_PLAYING:
            # Bajamos el reloj del cooldown si es mayor a cero
            if self.wall_sound_cooldown > 0:
                self.wall_sound_cooldown -= dt
                
            # Revisamos si alguna paleta tiene que encogerse (cooldown de 0.1s)
            for p in [self.paddle1, self.paddle2]:
                if p.shield_shrink_timer > 0:
                    p.shield_shrink_timer -= dt
                    if p.shield_shrink_timer <= 0:
                        p.power_active = POWER_NONE 
                        p.rect.height = PADDLE_HEIGHT # ¡Ahora sí encogemos la paleta!
                        p.color = WHITE               # Vuelve a ser blanca
                
                # ¡NUEVO! Lógica del Reloj Blanco (Crecimiento suave)
                if p.white_activation_timer > 0:
                    p.white_activation_timer -= dt
                    if p.white_activation_timer <= 0:
                        # La paleta ahora ocupa TODA la mitad de la cancha
                        p.rect.height = SCREEN_HEIGHT
                        p.rect.width = SCREEN_WIDTH // 2
                        p.rect.y = 0
                        p.y_float = 0.0
                        if p == self.paddle1:
                            p.rect.x = 0
                        else:
                            p.rect.x = SCREEN_WIDTH // 2
                        p.white_zone_hits_left = 5
                
            # Calculamos si la pelota está adentro de una Zona Alterada
            zone_multiplier = 1.0
            
            in_player1_side = (self.ball.rect.centerx < SCREEN_WIDTH // 2)
            in_player2_side = (self.ball.rect.centerx > SCREEN_WIDTH // 2)
            
            # --- NUEVA LÓGICA DE MULTIPLICADORES POR LADO ---
            z_type = 0
            if self.watches_kept_enabled:
                if in_player1_side: z_type = self.p1_zone_type
                else: z_type = self.p2_zone_type
            else:
                # Lógica clásica: solo si la pelota está en el lado del dueño
                if (self.slow_zone_owner == 1 and in_player1_side) or (self.slow_zone_owner == 2 and in_player2_side):
                    z_type = self.zone_type

            if z_type == 1: zone_multiplier = 0.5  # Azul
            elif z_type == 2: zone_multiplier = 1.25 # Rojo
                
            # --- LÓGICA DEL IMÁN (REFINADA) ---
            for i, p in enumerate([self.paddle1, self.paddle2]):
                player_id = i + 1
                is_on_side = (player_id == 1 and in_player1_side) or (player_id == 2 and in_player2_side)
                
                if p.power_active == POWER_MAGNET and is_on_side:
                    # Determinamos si la bola viene (Atracción) o se va (Guía)
                    is_incoming = (player_id == 1 and self.ball.vx < 0) or (player_id == 2 and self.ball.vx > 0)
                    
                    target_y = p.rect.centery
                    # 1. Calculamos la velocidad total actual para conservarla
                    current_speed = math.sqrt(self.ball.vx**2 + self.ball.vy**2)
                    
                    # 2. Vector hacia el centro de la paleta
                    dx = p.rect.centerx - self.ball.rect.centerx
                    dy = p.rect.centery - self.ball.rect.centery
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist > 0:
                        if is_incoming:
                            # MODO DEFENSA: Atracción planetaria (Curvamos la trayectoria hacia la paleta)
                            target_vx = (dx / dist) * current_speed
                            target_vy = (dy / dist) * current_speed
                            
                            # La pelota "cae" hacia la paleta (0.2 es la fuerza de gravedad)
                            self.ball.vx += (target_vx - self.ball.vx) * 0.2 * dt * 60
                            self.ball.vy += (target_vy - self.ball.vy) * 0.2 * dt * 60
                        else:
                            # MODO ATAQUE: Control de trayectoria (La pelota sigue el eje Y de la paleta)
                            # Solo afectamos la VY para que no vuelva hacia atrás, solo se curve
                            target_vy = (dy / dist) * current_speed
                            self.ball.vy += (target_vy - self.ball.vy) * 0.1 * dt * 60
                    
                    # 3. NORMALIZACIÓN: Forzamos a que la velocidad sea SIEMPRE la original
                    new_speed = math.sqrt(self.ball.vx**2 + self.ball.vy**2)
                    if new_speed > 0:
                        self.ball.vx = (self.ball.vx / new_speed) * current_speed
                        self.ball.vy = (self.ball.vy / new_speed) * current_speed
                    
                    # Efecto visual: azul eléctrico constante mientras hay magnetismo
                    self.ball.color = (100, 200, 255)
                elif not is_on_side and p.power_active == POWER_MAGNET:
                    # Si la bola salió de nuestro lado, recupera su color original (si no tiene otros poderes)
                    if not self.ball.is_fireball and not self.ball.is_orange:
                        self.ball.color = WHITE

            self.ball.update(dt, zone_multiplier) 
            self.check_collisions() 

    def draw_dashed_line(self, surface, color, start_pos, end_pos, width=1, dash_length=10):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dl = dash_length

        if (x1 == x2):
            ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
            xcoords = [x1] * len(ycoords)
        elif (y1 == y2):
            xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
            ycoords = [y1] * len(xcoords)
        else:
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            c = round(math.sqrt(a**2 + b**2))
            dx = dl * a / c
            dy = dl * b / c
            xcoords = [x for x in range(x1, x2, round(dx) if x1 < x2 else -round(dx))]
            ycoords = [y for y in range(y1, y2, round(dy) if y1 < y2 else -round(dy))]

        next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
        last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
        for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
            start = (round(x1), round(y1))
            end = (round(x2), round(y2))
            pygame.draw.line(surface, color, start, end, width)

    def draw(self):
        self.screen.fill(BLACK) 
        
        # Solo dibujamos la cancha si estamos en juego, saque, game over o en el menú principal
        if self.state in [STATE_PLAYING, STATE_SERVE, STATE_PRESS_TO_START, STATE_GAME_OVER, STATE_MAIN_MENU]:
            # Dibujamos las Zonas Alteradas
            def draw_zone(owner, z_type):
                if z_type == 1: color_z = (0, 0, 80)
                elif z_type == 2: color_z = (80, 0, 0)
                elif z_type == 3: color_z = VIOLET_ZONE
                elif z_type == 4: color_z = WHITE
                else: return

                rect_z = (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT) if owner == 1 else (SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)
                pygame.draw.rect(self.screen, color_z, rect_z)

            if self.watches_kept_enabled:
                draw_zone(1, self.p1_zone_type)
                draw_zone(2, self.p2_zone_type)
            elif self.slow_zone_owner != 0:
                draw_zone(self.slow_zone_owner, self.zone_type)
                
            self.draw_dashed_line(self.screen, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), width=2, dash_length=15)
            
            # Dibujamos el Reloj de Arena en el centro si corresponde (ESTILO PIXEL ART)
            if self.hourglass_rect:
                # Matriz de 9x7 (1 = pintar píxel, 0 = vacío)
                pixel_art = [
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
                
                pixel_size = 4 # Tamaño de cada "cuadradito" en pantalla
                
                # Decidimos el color dependiendo del tipo
                color_reloj = (50, 150, 255) # Por defecto azul
                if self.hourglass_type == 2: color_reloj = (255, 50, 50) # Rojo
                elif self.hourglass_type == 3: color_reloj = PURPLE
                elif self.hourglass_type == 4: color_reloj = WHITE
                elif self.hourglass_type == 5: color_reloj = YELLOW
                elif self.hourglass_type == 6: color_reloj = ORANGE
                
                # Calculamos dónde empezar a dibujar para que quede bien centrado
                start_x = self.hourglass_rect.centerx - (len(pixel_art[0]) * pixel_size) // 2
                start_y = self.hourglass_rect.centery - (len(pixel_art) * pixel_size) // 2
                
                # Recorremos el dibujo cuadrito por cuadrito
                for fila in range(len(pixel_art)):
                    for col in range(len(pixel_art[fila])):
                        if pixel_art[fila][col] == 1:
                            px = start_x + (col * pixel_size)
                            py = start_y + (fila * pixel_size)
                            pygame.draw.rect(self.screen, color_reloj, (px, py, pixel_size, pixel_size))
            
            self.paddle1.draw(self.screen)
            self.paddle2.draw(self.screen)
            
            # --- Dibujo de la Barrera Amarilla (Crucifijo / Vida Extra) ---
            if self.paddle1.has_extra_life:
                # Barrera detrás del Jugador 1 (Izquierda)
                pygame.draw.line(self.screen, YELLOW, (2, 0), (2, SCREEN_HEIGHT), 5)
            if self.paddle2.has_extra_life:
                # Barrera detrás del Jugador 2 (Derecha)
                pygame.draw.line(self.screen, YELLOW, (SCREEN_WIDTH - 2, 0), (SCREEN_WIDTH - 2, SCREEN_HEIGHT), 5)
            
            if self.state in [STATE_PLAYING, STATE_SERVE]:
                self.ball.draw(self.screen)
            elif self.state == STATE_PRESS_TO_START:
                # Texto de ayuda para el saque
                start_text = self.font.render("Presiona ESPACIO para Sacar", True, WHITE)
                start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                self.screen.blit(start_text, start_rect)

            # --- Dibujo del Marcador Dinámico (AL FINAL PARA QUE ESTÉ AL FRENTE) ---
            if self.watches_kept_enabled:
                color_score1 = BLACK if self.p1_zone_type == 4 else WHITE
                color_score2 = BLACK if self.p2_zone_type == 4 else WHITE
            else:
                color_score1 = BLACK if (self.zone_type == 4 and self.slow_zone_owner == 1) else WHITE
                color_score2 = BLACK if (self.zone_type == 4 and self.slow_zone_owner == 2) else WHITE
            
            score1_txt = self.font.render(str(self.score1), True, color_score1)
            score2_txt = self.font.render(str(self.score2), True, color_score2)
            
            self.screen.blit(score1_txt, (SCREEN_WIDTH // 2 - 70, 20))
            self.screen.blit(score2_txt, (SCREEN_WIDTH // 2 + 40, 20))

            # --- DIBUJO DE ANIMACIÓN MATCH POINT (Escalonado) ---
            if self.show_match_point_anim:
                anim_elapsed = 2.1 - self.match_point_anim_timer
                
                txt_match = self.large_font.render("MATCH", True, WHITE)
                txt_point = self.large_font.render("POINT", True, WHITE)
                
                # Calculamos el offset para que POINT empiece en la T de MATCH
                offset_t = self.large_font.render("MA", True, WHITE).get_width()
                
                # El ancho total del bloque es desde el inicio de MATCH hasta el final de POINT
                total_w = offset_t + txt_point.get_width()
                h_match = txt_match.get_height()
                
                # Lógica de movimiento: IN (0.8s), PAUSE (0.5s), OUT (0.8s)
                if anim_elapsed < 0.8:
                    t = anim_elapsed / 0.8
                    ease_out = 1 - (1 - t) * (1 - t)
                    current_x = SCREEN_WIDTH - (SCREEN_WIDTH // 2 + total_w // 2) * ease_out
                elif anim_elapsed < 1.3:
                    current_x = SCREEN_WIDTH // 2 - total_w // 2
                else:
                    t = (anim_elapsed - 1.3) / 0.8
                    ease_in = t * t
                    current_x = (SCREEN_WIDTH // 2 - total_w // 2) - (SCREEN_WIDTH // 2 + total_w) * ease_in
                
                # Dibujamos las dos palabras escalonadas
                center_y = SCREEN_HEIGHT // 2
                self.screen.blit(txt_match, (current_x, center_y - h_match))
                self.screen.blit(txt_point, (current_x + offset_t, center_y))
            
            # --- ANIMACIÓN GOLDEN GOAL (DORADA) ---
            if self.show_golden_goal_anim:
                # Fondo dorado parpadeante suave
                if int(pygame.time.get_ticks() / 200) % 2 == 0:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.set_alpha(80)
                    overlay.fill(GOLD)
                    self.screen.blit(overlay, (0,0))
                
                # Texto GOLDEN GOAL (Dorado y Blanco)
                txt_golden = self.large_font.render("GOLDEN", True, GOLD)
                txt_goal = self.large_font.render(" GOAL", True, WHITE)
                
                total_w = txt_golden.get_width() + txt_goal.get_width()
                start_x = SCREEN_WIDTH // 2 - total_w // 2
                center_y = SCREEN_HEIGHT // 2
                
                # Sombra para legibilidad
                s_golden = self.large_font.render("GOLDEN", True, BLACK)
                s_goal = self.large_font.render(" GOAL", True, BLACK)
                y_pos = center_y - txt_golden.get_height() // 2
                
                self.screen.blit(s_golden, (start_x + 4, y_pos + 4))
                self.screen.blit(s_goal, (start_x + txt_golden.get_width() + 4, y_pos + 4))
                
                # Texto Principal
                self.screen.blit(txt_golden, (start_x, y_pos))
                self.screen.blit(txt_goal, (start_x + txt_golden.get_width(), y_pos))
                
        if self.state == STATE_MAIN_MENU:
            # Efecto de oscurecido sobre la cancha
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(160) # Nivel de oscuridad (0 a 255)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))

            # Título y Botones del Menú Principal
            # Título: PONG KOMBAT 3.0 (Con "KOMBAT" en Rojo)
            pong_txt = self.large_font.render("PONG ", True, WHITE)
            kombat_txt = self.large_font.render("KOMBAT", True, RED)
            version_txt = self.large_font.render(" 3.0", True, WHITE)
            
            total_w = pong_txt.get_width() + kombat_txt.get_width() + version_txt.get_width()
            start_x = SCREEN_WIDTH // 2 - total_w // 2
            title_y = SCREEN_HEIGHT // 4
            
            self.screen.blit(pong_txt, (start_x, title_y - pong_txt.get_height() // 2))
            self.screen.blit(kombat_txt, (start_x + pong_txt.get_width(), title_y - kombat_txt.get_height() // 2))
            self.screen.blit(version_txt, (start_x + pong_txt.get_width() + kombat_txt.get_width(), title_y - version_txt.get_height() // 2))
            
            # Botón Play
            pygame.draw.rect(self.screen, BLACK, self.btn_play_rect)
            pygame.draw.rect(self.screen, WHITE, self.btn_play_rect, 4)
            play_text = self.font.render("PLAY", True, WHITE)
            play_rect = play_text.get_rect(center=self.btn_play_rect.center)
            self.screen.blit(play_text, play_rect)
            
            # Botón Modifiers
            pygame.draw.rect(self.screen, BLACK, self.btn_modifiers_rect)
            pygame.draw.rect(self.screen, WHITE, self.btn_modifiers_rect, 4)
            mod_text = self.font.render("MODIFIERS", True, WHITE)
            mod_rect = mod_text.get_rect(center=self.btn_modifiers_rect.center)
            self.screen.blit(mod_text, mod_rect)
            
        elif self.state == STATE_MODIFIERS:
            # Fondo del panel
            pygame.draw.rect(self.screen, BLACK, self.modifiers_panel_rect)
            pygame.draw.rect(self.screen, WHITE, self.modifiers_panel_rect, 4)
            
            # Título
            title_text = self.font.render("MATCH MODIFIERS", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.modifiers_panel_rect.y + 30))
            self.screen.blit(title_text, title_rect)
            
            # Botón BACK
            pygame.draw.rect(self.screen, BLACK, self.back_btn_rect)
            pygame.draw.rect(self.screen, WHITE, self.back_btn_rect, 2)
            back_text = self.small_font.render("BACK", True, WHITE)
            back_rect = back_text.get_rect(center=self.back_btn_rect.center)
            self.screen.blit(back_text, back_rect)
            
            # --- DIBUJO DE PESTAÑAS (TABS) ---
            tab_y = self.modifiers_panel_rect.top - 44
            self.tab_all_rect.topleft = (self.modifiers_panel_rect.left, tab_y)
            self.tab_extras_rect.topleft = (self.tab_all_rect.right + 5, tab_y)
            
            # Tab ALL
            bg_all = (40, 40, 40) if self.modifiers_tab == "ALL" else BLACK
            pygame.draw.rect(self.screen, bg_all, self.tab_all_rect, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(self.screen, WHITE, self.tab_all_rect, 2, border_top_left_radius=8, border_top_right_radius=8)
            t_all = self.small_font.render("ALL", True, WHITE)
            self.screen.blit(t_all, t_all.get_rect(center=self.tab_all_rect.center))
            
            # Tab EXTRAS (Verde un poco más claro)
            bg_ext = (0, 80, 0) if self.modifiers_tab == "EXTRAS" else (0, 40, 0)
            pygame.draw.rect(self.screen, bg_ext, self.tab_extras_rect, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(self.screen, WHITE, self.tab_extras_rect, 2, border_top_left_radius=8, border_top_right_radius=8)
            t_ext = self.small_font.render("EXTRAS", True, WHITE)
            self.screen.blit(t_ext, t_ext.get_rect(center=self.tab_extras_rect.center))

            # Clipping
            old_clip = self.screen.get_clip()
            clip_rect = pygame.Rect(self.modifiers_panel_rect.x + 10, self.modifiers_panel_rect.y + 60, 
                                    self.modifiers_panel_rect.width - 40, self.modifiers_panel_rect.height - 70)
            self.screen.set_clip(clip_rect)
            
            offset = self.scroll_y
            left_margin = self.modifiers_panel_rect.x + 50
            options_x = self.modifiers_panel_rect.centerx + 50
            max_y_rendered = 0
            
            def draw_rich_text(surface, text, pos, font, default_color=WHITE):
                import re
                # Dividimos el texto en palabras, pero manteniendo espacios, paréntesis, barras y pipes
                parts = re.split(r'(\s+|\(|\)|/|\|)', text)
                curr_x, curr_y = pos
                color_keywords = {
                    "BLUE": BLUE, "RED": RED, "PURPLE": PURPLE, "WHITE": WHITE,
                    "YELLOW": YELLOW, "ORANGE": ORANGE, "GREEN": GREEN, "CYAN": CYAN,
                    "GOLDEN": GOLD, "Golden": GOLD, "GOLD": GOLD, "MAG": BLUE, "NET": RED,
                    "Blue": BLUE, "Red": RED, "Purple": PURPLE, "White": WHITE,
                    "Yellow": YELLOW, "Orange": ORANGE, "Green": GREEN, "Cyan": CYAN
                }
                for part in parts:
                    if not part or part == "|": continue
                    color = color_keywords.get(part, default_color)
                    word_surf = font.render(part, True, color)
                    surface.blit(word_surf, (curr_x, curr_y))
                    curr_x += word_surf.get_width()

            def draw_remove_option(y_pos, text, enabled, rect, text_rect, is_checkbox=True, active_color=GREEN):
                nonlocal max_y_rendered
                ty = self.modifiers_panel_rect.y + y_pos - offset
                
                # Usar el nuevo sistema de texto enriquecido
                draw_rich_text(self.screen, text, (left_margin, ty), self.small_font)
                
                # El text_rect es para colisiones de tooltip (aproximado)
                text_rect.update(left_margin, ty, 300, 30) 
                
                if is_checkbox:
                    rect.update(options_x + 25, ty - 15, 30, 30)
                    pygame.draw.rect(self.screen, BLACK, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 2)
                    if enabled: pygame.draw.rect(self.screen, active_color, rect.inflate(-10, -10))
                else: rect.update(left_margin, ty, 300, 30)
                max_y_rendered = max(max_y_rendered, y_pos)

            if self.modifiers_tab == "ALL":
                # Usaremos current_y para que todo se posicione automáticamente
                current_y = 100
                
                # 1. Score Limit
                score_lbl = self.small_font.render("Score limit:", True, WHITE)
                self.screen.blit(score_lbl, (left_margin, self.modifiers_panel_rect.y + current_y - offset))
                self.score_btn_rect.update(options_x, self.modifiers_panel_rect.y + current_y - 5 - offset, 80, 40)
                pygame.draw.rect(self.screen, BLACK, self.score_btn_rect); pygame.draw.rect(self.screen, WHITE, self.score_btn_rect, 2)
                score_val = self.small_font.render(str(self.max_score), True, WHITE)
                self.screen.blit(score_val, score_val.get_rect(center=self.score_btn_rect.center))
                max_y_rendered = max(max_y_rendered, current_y)
                
                # 2. Ball Speed
                current_y += 80
                speed_lbl = self.small_font.render("Ball speed increase per hit:", True, WHITE)
                self.screen.blit(speed_lbl, (left_margin, self.modifiers_panel_rect.y + current_y - offset))
                self.ball_speed_btn_rect.update(options_x, self.modifiers_panel_rect.y + current_y - 5 - offset, 80, 40)
                pygame.draw.rect(self.screen, BLACK, self.ball_speed_btn_rect); pygame.draw.rect(self.screen, WHITE, self.ball_speed_btn_rect, 2)
                speed_val = self.small_font.render(str(self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]), True, WHITE)
                self.screen.blit(speed_val, speed_val.get_rect(center=self.ball_speed_btn_rect.center))
                max_y_rendered = max(max_y_rendered, current_y)

                # 3. Match Point
                current_y += 80
                draw_remove_option(current_y, "MATCH POINT:", self.match_point_enabled, self.match_point_rect, self.match_point_text_rect)
                
                # 4. Golden Goal Anim
                current_y += 80
                draw_remove_option(current_y, "Golden Goal Animation (5-5):", self.golden_goal_anim_enabled, self.golden_goal_anim_rect, self.golden_goal_anim_text_rect)
                
                # 5. Re-rolls
                current_y += 80
                draw_remove_option(current_y, "Re-rolls (Yellow/Orange):", self.reroll_enabled, self.reroll_rect, self.reroll_text_rect)
                
                # 6. All Re-roll
                if self.reroll_enabled:
                    current_y += 80
                    draw_remove_option(current_y, "All Re-roll (Red/Green):", self.all_reroll_enabled, self.all_reroll_rect, self.all_reroll_text_rect)
                else: self.all_reroll_rect.y = -1000
                
                # 7. Equal Weights
                current_y += 80
                draw_remove_option(current_y, "Equal watches (20% each):", self.equal_watches_enabled, self.equal_watches_rect, self.equal_watches_text_rect)
                current_y += 80
                draw_remove_option(current_y, "Equal power-ups (25% each):", self.equal_powers_enabled, self.equal_powers_rect, self.equal_powers_text_rect)
                
                # 8. Watches are kept
                current_y += 80
                draw_remove_option(current_y, "The watches are kept:", self.watches_kept_enabled, self.watches_kept_rect, self.watches_kept_text_rect)
                
                # 9. Watch spawn frequency (Relojes físicos)
                current_y += 80
                watch_lbl = self.small_font.render("Watch spawn frequency:", True, WHITE)
                self.screen.blit(watch_lbl, (left_margin, self.modifiers_panel_rect.y + current_y - offset))
                self.watch_spawn_hits_rect.update(options_x, self.modifiers_panel_rect.y + current_y - 5 - offset, 80, 40)
                pygame.draw.rect(self.screen, BLACK, self.watch_spawn_hits_rect); pygame.draw.rect(self.screen, WHITE, self.watch_spawn_hits_rect, 2)
                w_hits = self.watch_spawn_hits_options[self.watch_spawn_hits_idx]
                w_val_surf = self.small_font.render(str(w_hits), True, WHITE)
                self.screen.blit(w_val_surf, w_val_surf.get_rect(center=self.watch_spawn_hits_rect.center))
                self.watch_spawn_hits_text_rect.update(left_margin, self.modifiers_panel_rect.y + current_y - offset, watch_lbl.get_width(), watch_lbl.get_height())

                # 10. Power spawn frequency (Poder directo)
                current_y += 80
                pwr_lbl = self.small_font.render("Power spawn frequency:", True, WHITE)
                self.screen.blit(pwr_lbl, (left_margin, self.modifiers_panel_rect.y + current_y - offset))
                self.power_auto_grant_hits_rect.update(options_x, self.modifiers_panel_rect.y + current_y - 5 - offset, 80, 40)
                pygame.draw.rect(self.screen, BLACK, self.power_auto_grant_hits_rect); pygame.draw.rect(self.screen, WHITE, self.power_auto_grant_hits_rect, 2)
                p_hits = self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]
                p_val_surf = self.small_font.render(str(p_hits), True, WHITE)
                self.screen.blit(p_val_surf, p_val_surf.get_rect(center=self.power_auto_grant_hits_rect.center))
                self.power_auto_grant_hits_text_rect.update(left_margin, self.modifiers_panel_rect.y + current_y - offset, pwr_lbl.get_width(), pwr_lbl.get_height())
                
                # 11. Start with a power
                current_y += 80
                draw_remove_option(current_y, "Start with a Power:", self.start_with_power_enabled, self.start_with_power_rect, self.start_with_power_text_rect)
                
                max_y_rendered = max(max_y_rendered, current_y)

                # 10. Remove a watch (Toggle)
                current_y += 80
                w_txt = self.small_font.render("Remove a watch", True, WHITE)
                self.remove_watches_toggle_text_rect.update(w_txt.get_rect(midleft=(left_margin, self.modifiers_panel_rect.y + current_y - offset)))
                self.screen.blit(w_txt, self.remove_watches_toggle_text_rect)
                self.remove_watches_toggle_rect.update(options_x + 25, self.remove_watches_toggle_text_rect.centery - 15, 30, 30)
                pygame.draw.rect(self.screen, BLACK, self.remove_watches_toggle_rect); pygame.draw.rect(self.screen, WHITE, self.remove_watches_toggle_rect, 3)
                max_y_rendered = max(max_y_rendered, current_y)
                pcx, pcy = self.remove_watches_toggle_rect.center
                w = 8
                if self.remove_watches_expanded:
                    pygame.draw.line(self.screen, WHITE, (pcx-w, pcy+w//2), (pcx, pcy-w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx, pcy-w//2), (pcx+w, pcy+w//2), 3)
                    draw_remove_option(current_y + 60, "  - Remove Blue Watch", self.remove_blue, self.remove_blue_rect, self.remove_blue_text_rect, active_color=RED)
                    draw_remove_option(current_y + 120, "  - Remove Red Watch", self.remove_red, self.remove_red_rect, self.remove_red_text_rect, active_color=RED)
                    draw_remove_option(current_y + 180, "  - Remove Purple Watch", self.remove_purple, self.remove_purple_rect, self.remove_purple_text_rect, active_color=RED)
                    draw_remove_option(current_y + 240, "  - Remove White Watch", self.remove_white, self.remove_white_rect, self.remove_white_text_rect, active_color=RED)
                    draw_remove_option(current_y + 300, "  - Remove Yellow Watch", self.remove_yellow, self.remove_yellow_rect, self.remove_yellow_text_rect, active_color=RED)
                    current_y += 360
                else:
                    pygame.draw.line(self.screen, WHITE, (pcx-w, pcy-w//2), (pcx, pcy+w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx, pcy+w//2), (pcx+w, pcy-w//2), 3)
                    for r in [self.remove_blue_rect, self.remove_red_rect, self.remove_purple_rect, self.remove_white_rect, self.remove_yellow_rect]: r.y = -1000

                # 11. Remove a power (Toggle)
                current_y += 80
                p_txt = self.small_font.render("Remove a power", True, WHITE)
                self.remove_power_toggle_text_rect.update(p_txt.get_rect(midleft=(left_margin, self.modifiers_panel_rect.y + current_y - offset)))
                self.screen.blit(p_txt, self.remove_power_toggle_text_rect)
                self.remove_power_toggle_rect.update(options_x + 25, self.remove_power_toggle_text_rect.centery - 15, 30, 30)
                pygame.draw.rect(self.screen, BLACK, self.remove_power_toggle_rect); pygame.draw.rect(self.screen, WHITE, self.remove_power_toggle_rect, 3)
                max_y_rendered = max(max_y_rendered, current_y)
                pcx_p, pcy_p = self.remove_power_toggle_rect.center
                if self.remove_power_expanded:
                    pygame.draw.line(self.screen, WHITE, (pcx_p-w, pcy_p+w//2), (pcx_p, pcy_p-w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx_p, pcy_p-w//2), (pcx_p+w, pcy_p+w//2), 3)
                    draw_remove_option(current_y + 60, "  - Remove Red Power", self.remove_power_red, self.remove_power_red_rect, self.remove_power_red_text_rect, active_color=RED)
                    draw_remove_option(current_y + 120, "  - Remove Green Power", self.remove_power_green, self.remove_power_green_rect, self.remove_power_green_text_rect, active_color=RED)
                    draw_remove_option(current_y + 180, "  - Remove Yellow Power", self.remove_power_yellow, self.remove_power_yellow_rect, self.remove_power_yellow_text_rect, active_color=RED)
                    draw_remove_option(current_y + 240, "  - Remove Orange Power", self.remove_power_orange, self.remove_power_orange_rect, self.remove_power_orange_text_rect, active_color=RED)
                    current_y += 300
                else:
                    pygame.draw.line(self.screen, WHITE, (pcx_p-w, pcy_p-w//2), (pcx_p, pcy_p+w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx_p, pcy_p+w//2), (pcx_p+w, pcy_p-w//2), 3)
                    for r in [self.remove_power_red_rect, self.remove_power_green_rect, self.remove_power_yellow_rect, self.remove_power_orange_rect]: r.y = -1000

                # 12. Experimental Features (Toggle)
                current_y += 80
                exp_y = current_y
                exp_txt = self.small_font.render("Experimental Features", True, CYAN)
                self.experimental_toggle_text_rect.update(exp_txt.get_rect(midleft=(left_margin, self.modifiers_panel_rect.y + exp_y - offset)))
                self.screen.blit(exp_txt, self.experimental_toggle_text_rect)
                self.experimental_toggle_rect.update(options_x + 25, self.experimental_toggle_text_rect.centery - 15, 30, 30)
                pygame.draw.rect(self.screen, BLACK, self.experimental_toggle_rect); pygame.draw.rect(self.screen, WHITE, self.experimental_toggle_rect, 3)
                max_y_rendered = max(max_y_rendered, exp_y)
                pcx_e, pcy_e = self.experimental_toggle_rect.center
                if self.experimental_expanded:
                    pygame.draw.line(self.screen, WHITE, (pcx_e-w, pcy_e+w//2), (pcx_e, pcy_e-w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx_e, pcy_e-w//2), (pcx_e+w, pcy_e+w//2), 3)
                    draw_remove_option(exp_y + 60, "Enable Orange Watch", self.orange_watch_enabled, self.orange_watch_rect, self.orange_watch_text_rect, active_color=ORANGE)
                    draw_remove_option(exp_y + 120, "Enable MAG|NET Power", self.magnet_power_enabled, self.magnet_power_rect, self.magnet_power_text_rect, active_color=GRAY)
                    draw_remove_option(exp_y + 180, "Random GOLDEN Goal", self.experimental_golden_goal, self.experimental_golden_goal_rect, self.experimental_golden_goal_text_rect, active_color=GOLD)
                    current_y += 240
                else:
                    pygame.draw.line(self.screen, WHITE, (pcx_e-w, pcy_e-w//2), (pcx_e, pcy_e+w//2), 3); pygame.draw.line(self.screen, WHITE, (pcx_e, pcy_e+w//2), (pcx_e+w, pcy_e-w//2), 3)
                    for r in [self.orange_watch_rect, self.magnet_power_rect, self.experimental_golden_goal_rect]: r.y = -1000
                    self.orange_watch_text_rect.y = -1000


            elif self.modifiers_tab == "EXTRAS":
                # --- PESTAÑA EXTRAS: Acceso directo a Experimental Features ---
                extra_y = 100
                draw_remove_option(extra_y, "Enable Orange Watch", self.orange_watch_enabled, self.orange_watch_rect, self.orange_watch_text_rect, active_color=ORANGE)
                draw_remove_option(extra_y + 80, "Enable MAG|NET Power", self.magnet_power_enabled, self.magnet_power_rect, self.magnet_power_text_rect, active_color=GRAY)
                draw_remove_option(extra_y + 160, "Random GOLDEN Goal", self.experimental_golden_goal, self.experimental_golden_goal_rect, self.experimental_golden_goal_text_rect, active_color=GOLD)
                max_y_rendered = max(max_y_rendered, extra_y + 160)
                
                # Ocultar todos los rects de la otra pestaña
                for r in [self.match_point_rect, self.match_point_text_rect, self.golden_goal_anim_rect, self.golden_goal_anim_text_rect,
                          self.reroll_rect, self.reroll_text_rect, self.all_reroll_rect, self.all_reroll_text_rect, 
                          self.equal_watches_rect, self.equal_watches_text_rect, self.equal_powers_rect, self.equal_powers_text_rect, 
                          self.watches_kept_rect, self.watches_kept_text_rect, self.watch_spawn_hits_rect, self.watch_spawn_hits_text_rect,
                          self.remove_watches_toggle_rect, self.remove_watches_toggle_text_rect, 
                          self.remove_power_toggle_rect, self.remove_power_toggle_text_rect, 
                          self.experimental_toggle_rect, self.experimental_toggle_text_rect]: 
                    r.y = -1000
            # --- CÁLCULO DINÁMICO DEL SCROLL ---
            content_bottom = max_y_rendered + 60 
            calculated_max_scroll = max(0, content_bottom - 330)
            
            if self.max_scroll != calculated_max_scroll:
                self.max_scroll = calculated_max_scroll
                if self.scroll_y > self.max_scroll:
                    self.scroll_y = self.max_scroll
                scroll_fraction = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0
                self.scrollbar_thumb_rect.y = self.scrollbar_rect.top + scroll_fraction * (self.scrollbar_rect.height - self.scrollbar_thumb_height)
            
            # Restauramos el clip antes de dibujar tooltips
            self.screen.set_clip(old_clip)
            
            # Scrollbar
            pygame.draw.rect(self.screen, (50, 50, 50), self.scrollbar_rect)
            pygame.draw.rect(self.screen, WHITE, self.scrollbar_thumb_rect)
            
            # Hover Tooltips (Dibujar siempre AL FINAL para que quede por encima)
            mouse_pos = pygame.mouse.get_pos()
            tooltip_lines = []
            
            # SOLO procesamos si el ratón está dentro del área visible del panel (Clip Rect)
            if clip_rect.collidepoint(mouse_pos):
                # Filtramos por pestaña activa
                if self.modifiers_tab == "ALL":
                    if self.match_point_text_rect.collidepoint(mouse_pos) or self.match_point_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "If both players are one point away from winning (5-5),",
                            "the match will not end until one player gains a 2-point lead."
                        ]
                    elif self.golden_goal_anim_text_rect.collidepoint(mouse_pos) or self.golden_goal_anim_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "Shows a golden warning during critical moments",
                            "or sudden death rounds."
                        ]
                    elif self.reroll_text_rect.collidepoint(mouse_pos) or self.reroll_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "The orange and yellow power-ups will change into",
                            "another power-up after 2 hits."
                        ]
                    elif self.equal_watches_text_rect.collidepoint(mouse_pos) or self.equal_watches_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "All watches have a 20% chance of appearing."
                        ]
                    elif self.equal_powers_text_rect.collidepoint(mouse_pos) or self.equal_powers_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "All power-ups (Red, Green, Yellow, Orange)",
                            "have a 25% chance of appearing."
                        ]
                    elif self.watches_kept_text_rect.collidepoint(mouse_pos) or self.watches_kept_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "Picking up a new watch DOES NOT cancel",
                            "the opponent's active zone effect."
                        ]
                    elif self.watch_spawn_hits_text_rect.collidepoint(mouse_pos) or self.watch_spawn_hits_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "How many paddle hits are needed",
                            "to spawn a random Watch on the field."
                        ]
                    elif self.power_auto_grant_hits_text_rect.collidepoint(mouse_pos) or self.power_auto_grant_hits_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "How many paddle hits are needed",
                            "to grant a random power-up directly."
                        ]
                    elif self.start_with_power_text_rect.collidepoint(mouse_pos) or self.start_with_power_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "Both players start each round with a",
                            "random power-up if enabled."
                        ]
                    elif self.remove_power_toggle_text_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["Expand to disable specific paddle powers."]
                    elif self.remove_power_red_text_rect.collidepoint(mouse_pos) or self.remove_power_red_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["Fireball Power will never appear."]
                    elif self.remove_power_green_text_rect.collidepoint(mouse_pos) or self.remove_power_green_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["Giant Shield Power will never appear."]
                    elif self.remove_power_yellow_text_rect.collidepoint(mouse_pos) or self.remove_power_yellow_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["Speed Power will never appear."]
                    elif self.remove_power_orange_text_rect.collidepoint(mouse_pos) or self.remove_power_orange_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["Demolition Ball Power will never appear."]
                
                elif self.modifiers_tab == "EXTRAS":
                    if self.experimental_toggle_text_rect.collidepoint(mouse_pos):
                        tooltip_lines = ["New and experimental game mechanics."]
                    elif self.orange_watch_text_rect.collidepoint(mouse_pos) or self.orange_watch_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "Orange Watch: If hit by the ball, it triggers",
                            "the Demolition Ball effect instantly!"
                        ]
                    elif self.magnet_power_text_rect.collidepoint(mouse_pos) or self.magnet_power_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "MAGNET: The ball is attracted to your paddle",
                            "center like a planet when in your zone.",
                            "Allows steering the ball after hitting it."
                        ]
                    elif self.experimental_golden_goal_text_rect.collidepoint(mouse_pos) or self.experimental_golden_goal_rect.collidepoint(mouse_pos):
                        tooltip_lines = [
                            "Random GOLDEN Goal: 10% chance per round",
                            "to become Sudden Death. Next goal wins the match!"
                        ]
                
            if tooltip_lines:
                # Renderizamos todas las líneas dinámicamente
                rendered_lines = [self.tiny_font.render(line, True, BLACK) for line in tooltip_lines]
                tooltip_w = max([t.get_width() for t in rendered_lines]) + 20
                tooltip_h = sum([t.get_height() for t in rendered_lines]) + 10 + (5 * len(rendered_lines))
                
                tooltip_x = mouse_pos[0] + 15
                tooltip_y = mouse_pos[1] + 15
                
                # Evitar que se salga de la pantalla
                if tooltip_x + tooltip_w > SCREEN_WIDTH:
                    tooltip_x = SCREEN_WIDTH - tooltip_w - 10
                if tooltip_y + tooltip_h > SCREEN_HEIGHT:
                    tooltip_y = SCREEN_HEIGHT - tooltip_h - 10
                    
                tooltip_bg = pygame.Rect(tooltip_x, tooltip_y, tooltip_w, tooltip_h)
                pygame.draw.rect(self.screen, WHITE, tooltip_bg)
                pygame.draw.rect(self.screen, BLACK, tooltip_bg, 2)
                
                # Dibujamos las líneas
                current_y = tooltip_y + 10
                for rendered_text in rendered_lines:
                    self.screen.blit(rendered_text, (tooltip_x + 10, current_y))
                    current_y += rendered_text.get_height() + 5
            
        if self.state == STATE_GAME_OVER:
            # Efecto de oscurecido sobre la cancha congelada
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(160) # Nivel de oscuridad (0 a 255)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))

            if "\n" in self.winner_text:
                parts = self.winner_text.split("\n")
                # Línea 1: Grande
                win_text = self.large_font.render(parts[0], True, WHITE)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                self.screen.blit(win_text, win_rect)
                
                # Línea 2: Pequeña y entre paréntesis
                sub_text = self.small_font.render(parts[1], True, GOLD if "GOLDEN" in parts[1] else WHITE)
                sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, win_rect.bottom + 30))
                self.screen.blit(sub_text, sub_rect)
            else:
                win_text = self.large_font.render(self.winner_text, True, WHITE)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                self.screen.blit(win_text, win_rect)
            
            # Botón Restart
            pygame.draw.rect(self.screen, BLACK, self.btn_gameover_restart)
            pygame.draw.rect(self.screen, WHITE, self.btn_gameover_restart, 4)
            restart_text = self.font.render("Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=self.btn_gameover_restart.center)
            self.screen.blit(restart_text, restart_rect)
            
            # Botón Back to menu
            pygame.draw.rect(self.screen, BLACK, self.btn_gameover_menu)
            pygame.draw.rect(self.screen, WHITE, self.btn_gameover_menu, 4)
            menu_text = self.font.render("Back to menu", True, WHITE)
            menu_rect = menu_text.get_rect(center=self.btn_gameover_menu.center)
            self.screen.blit(menu_text, menu_rect)

        pygame.display.flip() 

    def run(self):
        while True: 
            dt = self.clock.tick(FPS) / 1000.0 
            self.handle_input(dt) 
            self.update(dt)       
            self.draw()           

if __name__ == "__main__":
    game = Game() 
    game.run()
