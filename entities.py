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
            (POWER_MAGNET, GRAY, 25 if game.equal_powers_enabled else 15, not game.magnet_power_enabled)
        ]
        available_powers = [p for p in all_p if not p[3]]
        if not available_powers: return
        total_weight = sum(p[2] for p in available_powers)
        r = random.random() * total_weight
        acc = 0
        for p_type, p_color, weight, removed in available_powers:
            acc += weight
            if r <= acc:
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
                self.speed_multiplier += 0.5
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

    def reset_orange(self, ball_size):
        if self.is_orange:
            self.rect.width = ball_size
            self.rect.height = ball_size
            self.speed /= 1.5
            self.is_orange = False
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
        angle = random.uniform(-math.pi/4, math.pi/4) 
        self.vx = self.speed * math.cos(angle) * direction_x
        self.vy = self.speed * math.sin(angle)

    def update(self, dt, speed_multiplier=1.0):
        self.x_float += self.vx * speed_multiplier * dt
        self.y_float += self.vy * speed_multiplier * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
