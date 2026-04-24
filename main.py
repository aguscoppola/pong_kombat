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

# Constantes de los Poderes (para que el código sea más fácil de leer)
POWER_NONE = 0       # Sin poder
POWER_FIREBALL = 1   # Poder de Bola de Fuego
POWER_SHIELD = 2     # Poder de Paleta Gigante
POWER_SPEED = 3      # ¡NUEVO! Poder Velocista (Amarillo)

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

# Reglas del juego
MAX_SCORE = 6 # Partidas más cortas e intensas 

# Estados del Juego
STATE_MENU = 0       
STATE_PLAYING = 1    
STATE_GAME_OVER = 2  
STATE_SERVE = 3      

# --- CLASES ---

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.y_float = float(y)
        
        # ¡Nuevas variables para la v2.0 Kombat!
        self.color = WHITE         # La paleta empieza siendo blanca
        self.hits = 0              # Contador de toques (empieza en 0)
        self.power_stored = POWER_NONE # Poder guardado listo para usarse
        self.power_active = POWER_NONE # Poder que se está usando AHORA mismo
        self.shield_hits_left = 0  # Cuántos golpes le quedan al escudo gigante
        self.shield_shrink_timer = 0.0 # ¡NUEVO! Tiempo de espera antes de encogerse
        self.speed_multiplier = 1.0    # Acumulable: 1.0 (Normal), 1.5 (+50%), 2.0 (+100%)
        self.yellow_power_hits = 0     # Contador de golpes sin activar para el "Reroll"

    # Función que reinicia la paleta cuando alguien anota un gol
    def reset(self):
        self.rect.height = PADDLE_HEIGHT # Vuelve al tamaño normal por las dudas
        self.color = WHITE               # Vuelve a ser blanca
        self.hits = 0                    # ¡Los toques vuelven a 0!
        self.power_stored = POWER_NONE
        self.power_active = POWER_NONE
        self.shield_hits_left = 0
        self.shield_shrink_timer = 0.0
        self.speed_multiplier = 1.0
        self.yellow_power_hits = 0
    
    # Función que activa el poder guardado cuando presionamos 'D' o 'L'
    def activate_power(self):
        # Solo lo activamos si teníamos un poder guardado
        if self.power_stored != POWER_NONE:
            self.power_active = self.power_stored # El poder pasa de "guardado" a "activo"
            self.power_stored = POWER_NONE        # Vaciamos la reserva
            
            # Si el poder que activamos es el Escudo Gigante...
            if self.power_active == POWER_SHIELD:
                self.rect.height = PADDLE_HEIGHT * 2 # ¡La paleta se hace el doble de alta!
                self.shield_hits_left = 2            # Nos va a durar 2 golpes
                
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
        # Ahora dibujamos la paleta usando su color dinámico (que puede ser blanco, rojo o verde)
        pygame.draw.rect(surface, self.color, self.rect)

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

    def serve(self, direction_x):
        self.rect.center = (self.start_x, self.start_y)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.speed = BALL_START_SPEED 
        
        # Reiniciamos el estado de la pelota en cada saque
        self.color = WHITE
        self.is_fireball = False
        
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
        pygame.display.set_caption("Pong Kombat v2.0") # ¡Subimos de versión!
        
        self.clock = pygame.time.Clock() 
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 72, bold=True)
        
        self.paddle1 = Paddle(PADDLE_OFFSET, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.score1 = 0
        self.score2 = 0
        
        self.state = STATE_MENU 
        self.serve_timer = 0    
        self.serve_direction = 1 
        self.winner_text = ""    
        
        # ¡NUEVO! Variables para el Reloj de Arena
        self.global_hits = 0        # Toques totales en la ronda
        self.hourglass_rect = None  # Si hay un reloj, guardamos su posición aquí
        self.hourglass_type = 0     # 1 = Reloj Azul, 2 = Reloj Rojo
        self.zone_type = 0          # 1 = Zona Azul (Lenta), 2 = Zona Roja (Rápida)
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
        
        self.state = STATE_SERVE 
        self.serve_timer = 1.0 
        self.serve_direction = random.choice([1, -1]) 
        self.ball.serve(self.serve_direction)

    def handle_input(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                elif self.state == STATE_GAME_OVER:
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
            else:
                self.error_sound.play() # Suena el error grave
                
            self.zone_type = self.hourglass_type # Copiamos el tipo de reloj a la zona
            self.hourglass_rect = None # Desaparece el reloj
            if self.last_hitter != 0:
                self.slow_zone_owner = self.last_hitter # Activamos la zona (Azul o Roja)

        # Colisiones de Gol
        if self.ball.rect.right < 0: 
            self.score2 += 1         
            self.goal_scored(-1)     
        elif self.ball.rect.left > SCREEN_WIDTH: 
            self.score1 += 1         
            self.goal_scored(1)      

        # Colisiones con las Paletas
        if self.ball.vx < 0 and self.ball.rect.colliderect(self.paddle1.rect):
            self.handle_paddle_collision(self.paddle1, 1) 
        elif self.ball.vx > 0 and self.ball.rect.colliderect(self.paddle2.rect):
            self.handle_paddle_collision(self.paddle2, -1) 

    def handle_paddle_collision(self, paddle, direction_x):
        # ¡NUEVO! Reproducimos el sonido de burbuja (POP) al tocar la paleta
        self.pop_sound.play() 
        
        # Guardamos quién le pegó y sumamos un toque global
        self.last_hitter = 1 if paddle == self.paddle1 else 2
        self.global_hits += 1
        
        # ¡NUEVO! Aparición Constante: A los 10 toques, y luego cada 5 toques (15, 20, 25...)
        if self.global_hits >= 10 and self.global_hits % 5 == 0:
            # Si no había reloj, lo creamos
            if self.hourglass_rect is None:
                self.hourglass_rect = pygame.Rect(SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 - 20, 30, 40)
            
            # Siempre que se cumpla esta condición, sorteamos el color de nuevo (Reroll o Nuevo Reloj)
            if random.random() < 0.75:
                self.hourglass_type = 1 # Azul
            else:
                self.hourglass_type = 2 # Rojo
        
        # 1. Si la pelota viene como Bola de Fuego (y acaba de chocar mi paleta), se apaga.
        if self.ball.is_fireball:
            self.ball.is_fireball = False
            self.ball.color = WHITE
            self.ball.speed /= 2 # Le quitamos la velocidad x2
            self.fire_sound.fadeout(500) # Hacemos que el sonido se desvanezca más rápido (0.5 seg)

        # 2. Aumento de dificultad estándar del Pong Clásico
        self.ball.speed *= BALL_SPEED_MULTIPLIER
        
        # 3. ¡Sumamos un golpe a la paleta!
        paddle.hits += 1
        
        # ¿Llegó a 7 golpes y NO tiene poderes encima?
        if paddle.hits >= 7:
            if paddle.power_stored == POWER_NONE and paddle.power_active == POWER_NONE:
                paddle.yellow_power_hits = 0 # Reiniciamos el contador por si le toca el amarillo
                
                # Sorteamos entre los 3 poderes (33% probabilidad c/u)
                paddle.power_stored = random.choice([POWER_FIREBALL, POWER_SHIELD, POWER_SPEED])
                
                # Le cambiamos el color a la paleta para avisarle al jugador
                if paddle.power_stored == POWER_FIREBALL:
                    paddle.color = RED
                elif paddle.power_stored == POWER_SHIELD:
                    paddle.color = GREEN
                elif paddle.power_stored == POWER_SPEED:
                    paddle.color = (255, 255, 0) # Amarillo Velocista
            
            # Reiniciamos sus toques a 0
            paddle.hits = 0

        # 4. Revisamos si la paleta tenía un poder ACTIVO listo para reaccionar al golpe
        if paddle.power_active == POWER_FIREBALL:
            paddle.power_active = POWER_NONE # Se gastó el poder
            paddle.color = WHITE             # Paleta vuelve a la normalidad
            self.ball.is_fireball = True     # ¡Bola se enciende!
            self.ball.color = RED
            self.ball.speed *= 2             # ¡Súper velocidad!
            self.fire_sound.play(-1)         # ¡NUEVO! Reproduce el fuego en bucle infinito (-1)
            
        elif paddle.power_active == POWER_SHIELD:
            paddle.shield_hits_left -= 1     # Gastamos 1 golpe del escudo gigante
            if paddle.shield_hits_left <= 0: # Si ya se acabaron los golpes...
                paddle.shield_shrink_timer = 0.1 # Iniciamos el cooldown de 0.1s
                # (No la encogemos aquí para evitar el bug matemático, se encoge en el update)

        # ¡NUEVO! Mecánica de Reroll del poder amarillo
        if paddle.power_stored == POWER_SPEED:
            paddle.yellow_power_hits += 1
            if paddle.yellow_power_hits >= 2: # Si golpeó 2 veces sin activarlo...
                # Se transforma al azar en Rojo o Verde
                if random.random() < 0.5:
                    paddle.power_stored = POWER_FIRE
                    paddle.color = (255, 50, 50)
                else:
                    paddle.power_stored = POWER_SHIELD
                    paddle.color = (50, 255, 50)
                paddle.yellow_power_hits = 0 # Reiniciamos el contador por si acaso
        
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

    def goal_scored(self, serve_direction):
        # Apagamos el fuego de a poco si alguien hace gol
        self.fire_sound.fadeout(500)
        
        # Reiniciamos las mecánicas globales
        self.global_hits = 0
        self.hourglass_rect = None
        self.hourglass_type = 0
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.last_hitter = 0
        
        # Cuando hay gol, borramos todos los poderes y toques de las paletas. ¡Empiezan limpios!
        self.paddle1.reset()
        self.paddle2.reset()
        
        if self.score1 >= MAX_SCORE:
            self.winner_text = "¡Jugador 1 Gana!"
            self.state = STATE_GAME_OVER 
        elif self.score2 >= MAX_SCORE:
            self.winner_text = "¡Jugador 2 Gana!"
            self.state = STATE_GAME_OVER 
        else:
            self.state = STATE_SERVE
            self.serve_timer = 1.0 
            self.serve_direction = serve_direction
            self.ball.serve(self.serve_direction)

    def update(self, dt):
        if self.state == STATE_SERVE:
            self.serve_timer -= dt 
            if self.serve_timer <= 0: 
                self.state = STATE_PLAYING 
                
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
                
            # Calculamos si la pelota está adentro de una Zona Alterada
            zone_multiplier = 1.0
            
            in_player1_side = (self.ball.rect.centerx < SCREEN_WIDTH // 2)
            in_player2_side = (self.ball.rect.centerx > SCREEN_WIDTH // 2)
            
            # Si la pelota está cruzando por la zona de quien la activó...
            if (self.slow_zone_owner == 1 and in_player1_side) or (self.slow_zone_owner == 2 and in_player2_side):
                if self.zone_type == 1:
                    zone_multiplier = 0.5  # Zona Azul: 50% de velocidad (Más lento, te ayuda)
                elif self.zone_type == 2:
                    zone_multiplier = 1.25 # Zona Roja: 25% MÁS velocidad (Más rápido, te perjudica)
                
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
        
        # Dibujamos la Zona Alterada si alguien la activó
        if self.slow_zone_owner != 0:
            color_zona = (0, 0, 80) if self.zone_type == 1 else (80, 0, 0) # Azul o Rojo oscuro
            
            if self.slow_zone_owner == 1:
                pygame.draw.rect(self.screen, color_zona, (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            elif self.slow_zone_owner == 2:
                pygame.draw.rect(self.screen, color_zona, (SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            
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
                [0,0,1,0,1,0,0],
                [0,1,1,1,1,1,0],
                [1,0,0,0,0,0,1],
                [1,1,1,1,1,1,1],
            ]
            
            pixel_size = 4 # Tamaño de cada "cuadradito" en pantalla
            
            # Decidimos el color dependiendo de si es el Bueno (Azul) o el Malo (Rojo)
            color_reloj = (50, 150, 255) if self.hourglass_type == 1 else (255, 50, 50)
            
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
        
        score_text = self.font.render(f"{self.score1}    {self.score2}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(score_text, score_rect) 
        
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        
        if self.state in [STATE_PLAYING, STATE_SERVE]:
            self.ball.draw(self.screen)
            
        if self.state == STATE_MENU:
            title_text = self.large_font.render("PONG KOMBAT v2.5", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            start_text = self.font.render("Presiona ESPACIO para Empezar", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(start_text, start_rect)
            
        elif self.state == STATE_GAME_OVER:
            win_text = self.large_font.render(self.winner_text, True, WHITE)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            restart_text = self.font.render("Presiona ESPACIO para Reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(win_text, win_rect)
            self.screen.blit(restart_text, restart_rect)

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
