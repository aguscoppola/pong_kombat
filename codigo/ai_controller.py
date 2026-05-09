import random
import math
from constants import *

class AIController:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        if not self.game.is_ai_mode:
            return

        # 1. Lógica de MAGNETO (Curvar pelota)
        if self.game.paddle2.power_active == POWER_MAGNET and self.game.balls:
            main_ball = self.game.balls[0]
            if main_ball.vx < 0: # La pelota se aleja de la IA hacia el jugador
                target_y = SCREEN_HEIGHT // 2
                if self.game.mouse:
                    target_y = 100 if self.game.mouse.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                else:
                    target_y = 50 if self.game.paddle1.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 50
                
                if self.game.paddle2.rect.centery < target_y: self.game.paddle2.move(1, dt, PADDLE_SPEED)
                elif self.game.paddle2.rect.centery > target_y: self.game.paddle2.move(-1, dt, PADDLE_SPEED)

        # 2. Lógica de CHICLE (Pegarse/Soltar)
        if self.game.paddle2.power_active == POWER_GUM:
            if self.game.paddle2.is_stuck:
                if self.game.mouse and self.game.mouse.rect.centerx > SCREEN_WIDTH // 2:
                    target_y = 100 if self.game.mouse.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                else:
                    target_y = 100 if self.game.paddle1.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                
                if self.game.paddle2.rect.centery < target_y - 10: self.game.paddle2.move(1, dt, PADDLE_SPEED)
                elif self.game.paddle2.rect.centery > target_y + 10: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
                
                if abs(self.game.paddle2.rect.centery - target_y) < 20 or self.game.paddle2.gum_charges <= 1:
                    if random.random() < 0.05: self.game.activate_paddle_power(self.game.paddle2, 2)
            else:
                if self.game.paddle2.gum_charges > 0 and random.random() < 0.01:
                    self.game.activate_paddle_power(self.game.paddle2, 2)

        # 3. PRIORIDAD ABSOLUTA: ESQUIVAR BALAS AMARILLAS
        yellow_bullets = [b for b in self.game.balls if b.is_bullet and b.vx > 0]
        if yellow_bullets:
            closest_bullet = min(yellow_bullets, key=lambda b: abs(b.rect.centerx - self.game.paddle2.rect.centerx))
            if closest_bullet.rect.centery < SCREEN_HEIGHT // 2: self.game.paddle2.move(1, dt, PADDLE_SPEED)
            else: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
            return # Centrarse solo en sobrevivir

        # 4. Lógica de REVOLVER
        if self.game.paddle2.power_active == POWER_REVOLVER and self.game.balls:
            main_ball = self.game.balls[0]
            if main_ball.vx > 0 and main_ball.rect.centerx > SCREEN_WIDTH * 0.4:
                target_y = main_ball.rect.centery
                if self.game.paddle2.rect.centery < target_y - 10: self.game.paddle2.move(1, dt, PADDLE_SPEED)
                elif self.game.paddle2.rect.centery > target_y + 10: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
            else:
                target_y = self.game.paddle1.rect.centery
                if self.game.paddle2.rect.centery < target_y - 5: self.game.paddle2.move(1, dt, PADDLE_SPEED)
                elif self.game.paddle2.rect.centery > target_y + 5: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
                if abs(self.game.paddle2.rect.centery - target_y) < 15:
                    if random.random() < 0.05: self.game.activate_paddle_power(self.game.paddle2, 2)
            return

        # 5. Esquivar bolas NARANJAS
        orange_threats = [b for b in self.game.balls if b.is_orange and b.vx > 0]
        if orange_threats:
            danger_ball = min(orange_threats, key=lambda b: abs(b.rect.centerx - self.game.paddle2.rect.centerx))
            if danger_ball.rect.centery < SCREEN_HEIGHT // 2: self.game.paddle2.move(1, dt, PADDLE_SPEED)
            else: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
            return

        # 6. Movimiento Estándar (Seguir Pelota / Anticipar Portales)
        if not self.game.paddle2.is_stuck:
            valid_balls = [b for b in self.game.balls if not (b.is_ghost and b.ghost_owner == 2)]
            if valid_balls:
                target_ball = min(valid_balls, key=lambda b: abs(b.rect.centerx - self.game.paddle2.rect.centerx))
                target_y = target_ball.rect.centery
                
                if self.game.portals_enabled:
                    portal_pairs = [(self.game.portal_blue_rect, self.game.portal_orange_rect), (self.game.portal_red_rect, self.game.portal_green_rect) if self.game.more_portals_enabled else (None, None)]
                    for p1, p2 in portal_pairs:
                        if p1 and p2:
                            if p1.inflate(20, 20).colliderect(target_ball.rect): target_y = p2.centery; break
                            elif p2.inflate(20, 20).colliderect(target_ball.rect): target_y = p1.centery; break

                aim_offset = 0
                if self.game.mouse: aim_offset = -self.game.paddle2.rect.height // 3 if self.game.mouse.rect.centery < target_ball.rect.centery else self.game.paddle2.rect.height // 3
                elif self.game.hourglass_rect and self.game.hourglass_type != 2: aim_offset = self.game.paddle2.rect.height // 3 if self.game.hourglass_rect.centery < target_ball.rect.centery else -self.game.paddle2.rect.height // 3
                elif self.game.score2 < self.game.score1 and self.game.is_x2_item_active: aim_offset = self.game.paddle2.rect.height // 3 if self.game.x2_item_rect.centery < target_ball.rect.centery else -self.game.paddle2.rect.height // 3

                if target_y < (self.game.paddle2.rect.centery + aim_offset) - 10: self.game.paddle2.move(-1, dt, PADDLE_SPEED)
                elif target_y > (self.game.paddle2.rect.centery + aim_offset) + 10: self.game.paddle2.move(1, dt, PADDLE_SPEED)
