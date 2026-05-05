import pygame
import random
import math
from constants import *

class Particle:
    def __init__(self, x, y, color, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.size = random.randint(3, 7)

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.lifetime -= dt

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.y_float = float(y)
        self.original_x = x
        self.color = WHITE
        self.hits = 0
        self.power_stored = POWER_NONE
        self.power_encapsulated = POWER_NONE
        self.encapsulated_color = WHITE
        self.power_active = POWER_NONE
        self.is_destroyed = False
        self.shield_hits_left = 0
        self.shield_shrink_timer = 0.0
        self.speed_multiplier = 1.0
        self.yellow_power_hits = 0
        self.orange_power_hits = 0
        self.red_power_hits = 0
        self.green_power_hits = 0
        self.has_extra_life = False
        self.white_zone_hits_left = 0
        self.white_activation_timer = 0.0

    def reset(self):
        self.rect.height = PADDLE_HEIGHT
        self.rect.width = PADDLE_WIDTH
        self.rect.x = self.original_x
        self.color = WHITE
        self.hits = 0
        self.power_stored = POWER_NONE
        self.power_encapsulated = POWER_NONE
        self.encapsulated_color = WHITE
        self.power_active = POWER_NONE
        self.shield_hits_left = 0
        self.shield_shrink_timer = 0.0
        self.speed_multiplier = 1.0
        self.yellow_power_hits = 0
        self.orange_power_hits = 0
        self.red_power_hits = 0
        self.green_power_hits = 0
        self.has_extra_life = False
        self.white_zone_hits_left = 0

    def grant_random_power(self, game):
        all_p = [
            (POWER_FIREBALL, RED, 25 if game.equal_powers_enabled else 30, game.remove_power_red),
            (POWER_SHIELD, GREEN, 25 if game.equal_powers_enabled else 30, game.remove_power_green),
            (POWER_SPEED, YELLOW, 25 if game.equal_powers_enabled else 30, game.remove_power_yellow),
            (POWER_ORANGE, ORANGE, 25 if game.equal_powers_enabled else 10, game.remove_power_orange),
            (POWER_MAGNET, GRAY, 25 if game.equal_powers_enabled else 15, not game.magnet_power_enabled),
            (POWER_GHOST, GHOST_COLOR, 25 if game.equal_powers_enabled else 15, not game.ghost_power_enabled)
        ]
        available_powers = [p for p in all_p if not p[3]]
        if not available_powers: return
        total_weight = sum(p[2] for p in available_powers)
        r = random.random() * total_weight
        acc = 0
        for p_type, p_color, weight, removed in available_powers:
            acc += weight
            if r <= acc:
                if game.encapsulate_powers_enabled:
                    if self.power_stored != POWER_NONE:
                        # Caso normal: Mover guardado a cápsula, nuevo a slot
                        self.power_encapsulated = self.power_stored
                        self.encapsulated_color = self.color
                        self.power_stored = p_type
                        self.color = p_color
                    elif self.power_active != POWER_NONE:
                        # Caso especial (BUG FIX): Si hay efecto activo, el nuevo va directo a cápsula
                        self.power_encapsulated = p_type
                        self.encapsulated_color = p_color
                    else:
                        # Caso simple: No hay nada, entra al slot
                        self.power_stored = p_type
                        self.color = p_color
                else:
                    # Sin modificador de cápsula: Sobreescribir siempre
                    self.power_stored = p_type
                    self.color = p_color
                break

    def activate_power(self, game):
        if self.power_stored != POWER_NONE:
            self.power_active = self.power_stored
            self.power_stored = POWER_NONE
            if self.power_active == POWER_SHIELD:
                self.rect.height = PADDLE_HEIGHT * 2
                self.shield_hits_left = 3
                if self.rect.bottom > SCREEN_HEIGHT:
                    self.rect.bottom = SCREEN_HEIGHT
                    self.y_float = float(self.rect.y)
            elif self.power_active == POWER_SPEED:
                self.speed_multiplier += game.yellow_speed_up_options[game.yellow_speed_up_idx]
                self.color = WHITE
                self.power_active = POWER_NONE
            elif self.power_active == POWER_MAGNET:
                self.magnet_hits_left = 3
                self.color = GRAY

    def move(self, direction, dt, paddle_speed):
        self.y_float += direction * (paddle_speed * self.speed_multiplier) * dt
        self.rect.y = int(self.y_float)
        if self.rect.top < 0: 
            self.rect.top = 0 
            self.y_float = float(self.rect.y)
        if self.rect.bottom > SCREEN_HEIGHT: 
            self.rect.bottom = SCREEN_HEIGHT 
            self.y_float = float(self.rect.y)

    def update(self, dt, game):
        # Recuperar poder encapsulado SOLO si la paleta está libre Y no hay ningún poder activo con duración
        if game.encapsulate_powers_enabled and self.power_stored == POWER_NONE and self.power_encapsulated != POWER_NONE:
            if self.power_active == POWER_NONE:
                self.power_stored = self.power_encapsulated
                self.color = self.encapsulated_color
                self.power_encapsulated = POWER_NONE
                self.encapsulated_color = WHITE

    def draw(self, surface, game):
        if self.is_destroyed: return
        if self.power_active == POWER_ORANGE and game.orange_skin_idx == 1:
            pygame.draw.rect(surface, WHITE, self.rect)
            belt_h = 10
            belt_y = self.rect.centery - belt_h // 2
            pygame.draw.rect(surface, RED, (self.rect.x, belt_y, self.rect.width, belt_h))
            pygame.draw.rect(surface, BLACK, self.rect, 1)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.power_active == POWER_MAGNET:
            pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y, self.rect.width, 10))
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
        self.speed = 0
        self.color = WHITE
        self.is_fireball = False
        self.is_orange = False
        self.is_ghost = False
        self.is_cheese = False
        self.ghost_owner = 0
        self.last_portal_id = None # Puede ser "blue", "orange" o None

    def reset_orange(self, ball_size):
        if self.is_orange:
            self.rect.width = ball_size
            self.rect.height = ball_size
            self.speed /= 1.5
            self.is_orange = False
            self.is_cheese = False
            self.color = WHITE

    def serve(self, direction_x, start_speed):
        self.rect.width = BALL_SIZE
        self.rect.height = BALL_SIZE
        self.rect.center = (self.start_x, self.start_y)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.speed = start_speed
        self.color = WHITE
        self.is_fireball = False
        self.is_orange = False
        self.is_cheese = False
        angle = random.uniform(-math.pi/4, math.pi/4) 
        self.vx = self.speed * math.cos(angle) * direction_x
        self.vy = self.speed * math.sin(angle)

    def update(self, dt, speed_multiplier=1.0):
        self.x_float += self.vx * speed_multiplier * dt
        self.y_float += self.vy * speed_multiplier * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def draw(self, surface, skin="Default"):
        if skin == "CHEESE":
            pygame.draw.rect(surface, YELLOW, self.rect)
            # Dibujar huecos de queso (pixeles naranja)
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 2, self.rect.y + 2, 2, 2))
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 6, self.rect.y + 5, 2, 2))
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 3, self.rect.y + 7, 1, 1))
        elif skin == "Tennis":
            pygame.draw.rect(surface, (173, 255, 47), self.rect) # Verde Tennis
            # Franja blanca "pixelada" diagonal
            px = self.rect.width // 5
            pygame.draw.rect(surface, WHITE, (self.rect.x, self.rect.y + px, px, px))
            pygame.draw.rect(surface, WHITE, (self.rect.x + px, self.rect.y + 2*px, px, px))
            pygame.draw.rect(surface, WHITE, (self.rect.x + 2*px, self.rect.y + 2*px, px, px))
            pygame.draw.rect(surface, WHITE, (self.rect.x + 3*px, self.rect.y + px, px, px))
            pygame.draw.rect(surface, WHITE, (self.rect.x + 4*px, self.rect.y, px, px))
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        
        if self.is_cheese and skin != "CHEESE":
            # Si el ratón está activo pero la skin no es queso, aplicamos los huecos encima
            pygame.draw.rect(surface, YELLOW, self.rect)
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 2, self.rect.y + 2, 2, 2))
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 6, self.rect.y + 5, 2, 2))
            pygame.draw.rect(surface, ORANGE, (self.rect.x + 3, self.rect.y + 7, 1, 1))

class Mouse:
    def __init__(self, x, y):
        self.size = 30
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.color = (150, 150, 150) # Gris
        self.tail_color = (255, 182, 193) # Rosa
        self.speed = 0
        self.facing_right = True

    def update(self, dt, target_ball, speed_multiplier=0.5):
        # Velocidad basada en la pelota y el multiplicador configurado
        self.speed = target_ball.speed * speed_multiplier
        
        # Objetivo: el centro de la pelota
        target_x = target_ball.rect.centerx
        target_y = target_ball.rect.centery
        
        # Orientación
        self.facing_right = target_x > self.rect.centerx
        
        # Posición actual: nuestro centro
        current_x = self.x_float + self.size / 2
        current_y = self.y_float + self.size / 2
        
        dx = target_x - current_x
        dy = target_y - current_y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            move_dist = self.speed * dt
            if move_dist > dist: # Evitar orbitar
                self.x_float = target_x - self.size / 2
                self.y_float = target_y - self.size / 2
            else:
                self.x_float += (dx / dist) * move_dist
                self.y_float += (dy / dist) * move_dist
            
            self.rect.x = int(self.x_float)
            self.rect.y = int(self.y_float)

    def draw(self, surface):
        # Cuerpo del ratón (30x30)
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Orientación de los detalles
        if self.facing_right:
            tx = self.rect.left - 9 # Cola a la izquierda
            nx = self.rect.right - 4 # Nariz a la derecha
            w_dir = 1
        else:
            tx = self.rect.right # Cola a la derecha
            nx = self.rect.left # Nariz a la izquierda
            w_dir = -1
            
        ty = self.rect.centery - 4
        
        # 1. La cola (un cuadrado de 9x9 dividido en 3 franjas verticales)
        pygame.draw.rect(surface, (255, 0, 255), (tx, ty, 3, 9))
        pygame.draw.rect(surface, (255, 182, 193), (tx + 3, ty, 3, 9))
        pygame.draw.rect(surface, (255, 0, 255), (tx + 6, ty, 3, 9))
        
        # 2. La nariz (Negra, dentro del cuerpo)
        n_x = self.rect.right - 9 if self.facing_right else self.rect.left
        pygame.draw.rect(surface, BLACK, (n_x, self.rect.centery - 4, 9, 9))
        
        # 3. Los bigotes (líneas grises oscuras, dentro del cuerpo)
        b_col = (80, 80, 80)
        # Punto de origen (base de la nariz)
        origin_x = self.rect.right - 9 if self.facing_right else self.rect.left + 9
        # Punto final (más cortos ahora, hacia el interior)
        target_x = self.rect.right - 17 if self.facing_right else self.rect.left + 17
        
        # Bigote superior
        pygame.draw.line(surface, b_col, (origin_x, self.rect.centery - 2), (target_x, self.rect.centery - 8), 4)
        # Bigote inferior
        pygame.draw.line(surface, b_col, (origin_x, self.rect.centery + 2), (target_x, self.rect.centery + 8), 4)
