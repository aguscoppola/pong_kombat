import pygame
import random
import math
from constants import *

class Particle:
    def __init__(self, x, y, color, lifetime=1.0, is_confetti=False):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.is_confetti = is_confetti
        
        if is_confetti:
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(2, 5) # Caída constante
            self.size = random.randint(4, 8)
        else:
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
        self.white_zone_shrink_timer = 0.0
        # Variables para GUM Power
        self.gum_charges = 0
        self.is_stuck = False
        self.stuck_ball = None
        self.gum_decay_timer = 0.0
        # Variables para REVOLVER
        self.revolver_shots_left = 0
        self.revolver_timer = 0.0
        # Variables para SLEEP (v0.6.0)
        self.sleep_hits_left = 0
        self.sleep_timer = 0.0

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
        self.white_zone_shrink_timer = 0.0
        self.gum_charges = 0
        self.is_stuck = False
        self.stuck_ball = None
        self.gum_decay_timer = 0.0
        self.revolver_shots_left = 0
        self.revolver_timer = 0.0
        self.sleep_hits_left = 0
        self.sleep_timer = 0.0

    def grant_random_power(self, game):
        all_p = [
            (POWER_FIREBALL, RED, 25 if game.equal_powers_enabled else 30, game.remove_power_red),
            (POWER_SHIELD, GREEN, 25 if game.equal_powers_enabled else 30, game.remove_power_green),
            (POWER_SPEED, YELLOW, 25 if game.equal_powers_enabled else 30, game.remove_power_yellow),
            (POWER_ORANGE, ORANGE, 25 if game.equal_powers_enabled else 10, game.remove_power_orange),
            (POWER_MAGNET, GRAY, 25 if game.equal_powers_enabled else 15, not game.magnet_power_enabled),
            (POWER_GHOST, GHOST_COLOR, 25 if game.equal_powers_enabled else 15, not game.ghost_power_enabled),
            (POWER_GUM, GUM_PINK, 25 if game.equal_powers_enabled else 15, not game.gum_power_enabled),
            (POWER_SLEEP, SLEEP_PURPLE, 25 if game.equal_powers_enabled else 10, not game.sleeping_power_enabled)
        ]
        available_powers = [p for p in all_p if not p[3]]
        if not available_powers: return
        total_weight = sum(p[2] for p in available_powers)
        r = random.random() * total_weight
        acc = 0
        for p_type, p_color, weight, removed in available_powers:
            acc += weight
            if r <= acc:
                # REGLA v0.6.0: Si hay un poder activo, NO recibir uno nuevo (vía hits) 
                # a menos que sea de contacto (ROJO o NARANJA)
                if self.power_active != POWER_NONE and p_type not in [POWER_FIREBALL, POWER_ORANGE]:
                    return # No recibimos nada
                
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
                
                # AUTO-ACTIVAR GUM POWER (v0.6.0: Si no hay otro activo ya)
                if p_type == POWER_GUM:
                    self.power_active = POWER_GUM
                    self.gum_charges = 3
                    self.color = GUM_PINK
                    self.power_stored = POWER_NONE
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
            elif self.power_active == POWER_REVOLVER:
                self.revolver_shots_left = 3
                self.revolver_timer = 10.0
                self.color = GRAY
            elif self.power_active == POWER_SLEEP:
                self.color = SLEEP_PURPLE

    def move(self, direction, dt, paddle_speed):
        if self.sleep_hits_left > 0: return # Bloqueo por Sueño (v0.6.0)
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

        # Procesar encogimiento de Zona Blanca (Reloj Blanco)
        if self.white_zone_shrink_timer > 0:
            self.white_zone_shrink_timer -= dt
            if self.white_zone_shrink_timer <= 0:
                self.rect.height = PADDLE_HEIGHT
                self.rect.width = PADDLE_WIDTH
                if self.power_active == POWER_NONE: self.color = WHITE
                # Resetear posición x según el jugador
                if self.rect.x < SCREEN_WIDTH // 2: self.rect.x = 20
                else: self.rect.x = SCREEN_WIDTH - 20 - PADDLE_WIDTH
                self.y_float = float(self.rect.y)

        # Lógica de Pegado del Chicle
        if self.power_active == POWER_GUM and self.is_stuck and self.stuck_ball:
            # Sincronizar posición de la pelota
            self.stuck_ball.rect.centery = self.rect.centery
            if self.rect.x < SCREEN_WIDTH // 2: # J1
                self.stuck_ball.rect.left = self.rect.right
            else: # J2
                self.stuck_ball.rect.right = self.rect.left
            self.stuck_ball.x_float = float(self.stuck_ball.rect.x)
            self.stuck_ball.y_float = float(self.stuck_ball.rect.y)
            
            # Consumir cargas (1 por segundo)
            self.gum_decay_timer += dt
            if self.gum_decay_timer >= 1.0:
                self.gum_decay_timer = 0.0
                self.gum_charges -= 1
                if self.gum_charges <= 0:
                    self.is_stuck = False
                    # Impulso al soltarse
                    self.stuck_ball.vx = 400 if self.rect.x < SCREEN_WIDTH // 2 else -400
                    self.stuck_ball.vy = random.uniform(-100, 100)
                    self.stuck_ball = None
                    self.power_active = POWER_NONE
                    self.color = WHITE
        
        # Recuperación por tiempo del sueño (v0.6.0 Fix)
        if self.sleep_hits_left > 0:
            self.sleep_timer -= dt
            if self.sleep_timer <= 0:
                self.sleep_hits_left = 0

    def draw(self, surface, game):
        if self.is_destroyed: return
        if self.power_active == POWER_ORANGE and game.orange_skin_idx == 1:
            pygame.draw.rect(surface, WHITE, self.rect)
            belt_h = 10
            belt_y = self.rect.centery - belt_h // 2
            pygame.draw.rect(surface, RED, (self.rect.x, belt_y, self.rect.width, belt_h))
            pygame.draw.rect(surface, BLACK, self.rect, 1)
        elif self.power_active == POWER_REVOLVER:
            # 2/3 Gris Metal, 1/3 Marrón Empuñadura
            h_metal = (self.rect.height * 2) // 3
            h_handle = self.rect.height - h_metal
            pygame.draw.rect(surface, GUN_METAL, (self.rect.x, self.rect.y, self.rect.width, h_metal))
            pygame.draw.rect(surface, LIGHT_BROWN, (self.rect.x, self.rect.y + h_metal, self.rect.width, h_handle))
            pygame.draw.rect(surface, BLACK, self.rect, 1)
        elif self.power_active == POWER_GUM:
            # Dibujar en 3 bloques claros
            bh = self.rect.height // 3
            # Bloque 3 (Abajo) - Siempre rosa si tiene >= 1 carga
            c3 = GUM_PINK if self.gum_charges >= 1 else WHITE
            pygame.draw.rect(surface, c3, (self.rect.x, self.rect.y + bh*2, self.rect.width, self.rect.height - bh*2))
            # Bloque 2 (Medio) - Rosa si tiene >= 2 cargas
            c2 = GUM_PINK if self.gum_charges >= 2 else WHITE
            pygame.draw.rect(surface, c2, (self.rect.x, self.rect.y + bh, self.rect.width, bh))
            # Bloque 1 (Arriba) - Rosa si tiene 3 cargas
            c1 = GUM_PINK if self.gum_charges >= 3 else WHITE
            pygame.draw.rect(surface, c1, (self.rect.x, self.rect.y, self.rect.width, bh))
        elif self.sleep_hits_left > 0:
            # Dibujar paleta inmovilizada (Gris Violeta)
            pygame.draw.rect(surface, (120, 100, 150), self.rect)
            pygame.draw.rect(surface, SLEEP_PURPLE, self.rect, 2)
            # Dibujar ZZZ
            fz = pygame.font.SysFont("Arial", 16, bold=True)
            txt = fz.render("Zzz", True, WHITE)
            surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.power_active == POWER_MAGNET:
            pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y, self.rect.width, 10))
            pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.bottom - 10, self.rect.width, 10))

class SleepProjectile:
    def __init__(self, x, y, vx, vy, is_child=False):
        size = BALL_SIZE * 2 if not is_child else BALL_SIZE
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.vx = vx
        self.vy = vy
        self.active = True
        self.is_child = is_child
        self.split_done = False
        self.owner_immunity = 0.0
        self.owner_ref = None
        self.is_sleep = True

    def update(self, dt, game):
        if self.owner_immunity > 0:
            self.owner_immunity -= dt
            
        self.x_float += self.vx * dt
        self.y_float += self.vy * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)
        
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.active = False
            return

        if not self.is_child and not self.split_done:
            # Cruzar la mitad del mapa
            if (self.vx > 0 and self.rect.centerx > SCREEN_WIDTH // 2) or \
               (self.vx < 0 and self.rect.centerx < SCREEN_WIDTH // 2):
                self.split_done = True
                self.active = False
                # Crear 3 hijos (v0.6.0)
                speed = math.hypot(self.vx, self.vy)
                angle = math.atan2(self.vy, self.vx)
                for offset in [-math.pi/4, 0, math.pi/4]:
                    new_angle = angle + offset
                    game.sleep_projectiles.append(SleepProjectile(self.rect.centerx, self.rect.centery, 
                                                                 speed * math.cos(new_angle), 
                                                                 speed * math.sin(new_angle), is_child=True))

    def draw(self, surface):
        pygame.draw.rect(surface, SLEEP_PURPLE, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

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
        self.ghost_owner = 0
        self.is_cheese = False
        self.is_bullet = False
        self.is_kill_ball = False
        self.bullet_immunity = 0.0 # Cooldown para no matarse al disparar
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
        if self.bullet_immunity > 0: self.bullet_immunity -= dt
        self.x_float += self.vx * speed_multiplier * dt
        self.y_float += self.vy * speed_multiplier * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def draw(self, surface, skin="Default", identical_ghost=False, main_color=WHITE):
        draw_color = self.color
        if self.is_ghost:
            if not identical_ghost:
                pygame.draw.rect(surface, GHOST_COLOR, self.rect)
                pygame.draw.rect(surface, WHITE, self.rect, 1) # Borde sutil
                return
            else:
                draw_color = main_color
        
        if self.is_bullet:
            pygame.draw.rect(surface, YELLOW, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 1)
            return

        if skin == "CHEESE":
            # Cuña de queso base
            points = [(self.rect.centerx, self.rect.top), (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom)]
            pygame.draw.polygon(surface, YELLOW, points)
            
            # OJOS GIGANTES con brillo (3x4 pixels)
            # Ojo Izquierdo
            pygame.draw.rect(surface, BLACK, (self.rect.x + 1, self.rect.y + 2, 3, 4))
            pygame.draw.rect(surface, WHITE, (self.rect.x + 1, self.rect.y + 2, 1, 1)) # Brillo
            # Ojo Derecho
            pygame.draw.rect(surface, BLACK, (self.rect.x + 6, self.rect.y + 2, 3, 4))
            pygame.draw.rect(surface, WHITE, (self.rect.x + 6, self.rect.y + 2, 1, 1)) # Brillo
            
            # SONROJO GRANDE (Pinky)
            pygame.draw.rect(surface, (255, 120, 150), (self.rect.x, self.rect.y + 6, 2, 1))
            pygame.draw.rect(surface, (255, 120, 150), (self.rect.x + 8, self.rect.y + 6, 2, 1))
            
            # BOCA ABIERTA CUTE
            pygame.draw.rect(surface, BLACK, (self.rect.x + 4, self.rect.y + 7, 2, 2))
            pygame.draw.rect(surface, (255, 100, 100), (self.rect.x + 4, self.rect.y + 8, 2, 1)) # Lengüita
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
            pygame.draw.rect(surface, draw_color, self.rect)
        
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
        # Cuerpo blocky (Gris Pong)
        body_color = (180, 180, 180)
        pygame.draw.rect(surface, body_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2) # Borde para que resalte
        
        # Orejas de bloque gigantes (Desproporcionadas)
        ear_size = 12
        pygame.draw.rect(surface, body_color, (self.rect.left - 4, self.rect.top - 8, ear_size, ear_size))
        pygame.draw.rect(surface, body_color, (self.rect.right - ear_size + 4, self.rect.top - 8, ear_size, ear_size))
        # Interior orejas (Rosa pixelado)
        pygame.draw.rect(surface, (255, 150, 180), (self.rect.left - 2, self.rect.top - 6, ear_size - 4, ear_size - 4))
        pygame.draw.rect(surface, (255, 150, 180), (self.rect.right - ear_size + 6, self.rect.top - 6, ear_size - 4, ear_size - 4))

        # Cara Caricaturesca (Blocky)
        if self.facing_right:
            # OJOS CUADRADOS GIGANTES
            pygame.draw.rect(surface, WHITE, (self.rect.x + 15, self.rect.y + 2, 8, 8))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 19, self.rect.y + 4, 4, 4)) # Pupila
            # Nariz bloque
            pygame.draw.rect(surface, (255, 100, 150), (self.rect.right - 4, self.rect.centery, 4, 4))
            # Diente (Un solo bloque blanco)
            pygame.draw.rect(surface, WHITE, (self.rect.right - 8, self.rect.bottom - 4, 3, 3))
        else:
            # OJOS CUADRADOS GIGANTES
            pygame.draw.rect(surface, WHITE, (self.rect.x + 7, self.rect.y + 2, 8, 8))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 7, self.rect.y + 4, 4, 4)) # Pupila
            # Nariz bloque
            pygame.draw.rect(surface, (255, 100, 150), (self.rect.left, self.rect.centery, 4, 4))
            # Diente (Un solo bloque blanco)
            pygame.draw.rect(surface, WHITE, (self.rect.left + 5, self.rect.bottom - 4, 3, 3))

        # Cola segmentada (Estilo línea de Pong)
        tail_color = (255, 182, 193)
        tx = self.rect.left - 12 if self.facing_right else self.rect.right
        for i in range(3):
            pygame.draw.rect(surface, tail_color, (tx + i*4, self.rect.centery + 4, 3, 3))

class GumProjectile:
    def __init__(self, x, y, direction, owner):
        size = BALL_SIZE * 3
        self.rect = pygame.Rect(x, y - size//2, size, size)
        self.x_float = float(self.rect.x)
        self.vx = 500 * direction
        self.active = True
        self.owner = owner

    def update(self, dt):
        self.x_float += self.vx * dt
        self.rect.x = int(self.x_float)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, GUM_PINK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
class Cloud:
    def __init__(self, x, y, direction, size_mult=1.0, speed_mult=1.0):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.speed = random.uniform(80, 180) * speed_mult
        self.active = True
        
        # Generar forma "pixel art" abstracta (unión de rectángulos)
        self.rects = []
        num_blocks = random.randint(3, 7)
        base_w = int(random.randint(60, 120) * size_mult)
        base_h = int(random.randint(40, 80) * size_mult)
        
        for _ in range(num_blocks):
            w = random.randint(base_w // 2, base_w)
            h = random.randint(base_h // 2, base_h)
            ox = random.randint(-base_w // 2, base_w // 2)
            oy = random.randint(-base_h // 3, base_h // 3)
            self.rects.append(pygame.Rect(ox, oy, w, h))

    def update(self, dt):
        self.x += self.direction * self.speed * dt
        if self.direction > 0 and self.x > SCREEN_WIDTH + 200: self.active = False
        elif self.direction < 0 and self.x < -300: self.active = False

    def draw(self, surface):
        # Color Gris Sólido (Opacidad 100%)
        color = (100, 100, 100) # Gris estándar
        for r in self.rects:
            draw_r = r.copy()
            draw_r.x += int(self.x)
            draw_r.y += int(self.y)
            pygame.draw.rect(surface, color, draw_r)
