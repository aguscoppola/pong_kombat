import pygame
import math
import random
from constants import *

class PhysicsEngine:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        for ball in self.game.balls[:]:
            # 0. Actualizar posición (Fundamental para el movimiento)
            ball.update(dt, self.game._get_zone_multiplier(ball))
            # 1. Procesar físicas y colisiones
            self._process_ball_physics(ball, dt)
        
        # 3. Colisiones de Proyectiles de Sueño (v0.6.0)
        self._check_sleep_projectile_collisions()

    def _check_sleep_projectile_collisions(self):
        for sp in self.game.sleep_projectiles[:]:
            # Colisión con Paletas
            if sp.rect.colliderect(self.game.paddle1.rect):
                if sp.owner_ref == self.game.paddle1 and sp.owner_immunity > 0: continue
                self.game.audio.play('sleep') # v0.6.0 Fix: Nuevo sonido
                self.game.paddle1.sleep_hits_left = 2
                self.game.paddle1.sleep_timer = 4.0 # Ajustado a 4 segundos (v0.6.0 Fix)
                self.game.vfx.explosion(sp.rect.centerx, sp.rect.centery, SLEEP_PURPLE)
                sp.active = False
            elif sp.rect.colliderect(self.game.paddle2.rect):
                if sp.owner_ref == self.game.paddle2 and sp.owner_immunity > 0: continue
                self.game.audio.play('sleep') # v0.6.0 Fix: Nuevo sonido
                self.game.paddle2.sleep_hits_left = 2
                self.game.paddle2.sleep_timer = 4.0 # Ajustado a 4 segundos (v0.6.0 Fix)
                self.game.vfx.explosion(sp.rect.centerx, sp.rect.centery, SLEEP_PURPLE)
                sp.active = False

    def _process_ball_physics(self, ball, dt):
        # 1. Rebotes en Paredes (Superior/Inferior)
        if ball.rect.top < 0:
            ball.rect.top = 0
            ball.y_float = float(ball.rect.y)
            ball.vy = abs(ball.vy)
            if self.game.wall_sound_cooldown <= 0:
                self.game.audio.play('hit')
                self.game.wall_sound_cooldown = 0.25
        elif ball.rect.bottom > SCREEN_HEIGHT:
            ball.rect.bottom = SCREEN_HEIGHT
            ball.y_float = float(ball.rect.y)
            ball.vy = -abs(ball.vy)
            if self.game.wall_sound_cooldown <= 0:
                self.game.audio.play('hit')
                self.game.wall_sound_cooldown = 0.25

        # 2. Gravedad y Colisiones de Planetas
        if self.game.floating_planets_enabled:
            self._apply_planet_gravity(ball, dt)
            self._check_planet_collisions(ball)

        # 4. Colisiones con Portales
        if self.game.portals_enabled:
            self._check_portal_collisions(ball)

        # 4.5. Colisiones con Ta-Te-Ti
        if self.game.tictactoe_enabled:
            self._check_tictactoe_collisions(ball)

        # 5. Colisiones con Paletas, Goles y Objetos
        self._check_world_collisions(ball)

    def _check_tictactoe_collisions(self, ball):
        if self.game.tictactoe_enabled and self.game.tictactoe_win_timer <= 0.0:
            # Solo comprobar si la pelota está en el área central (310, 210, 180, 180)
            ball_rect = ball.rect
            grid_x, grid_y = 310, 210
            grid_w, grid_h = 180, 180
            if (ball_rect.right >= grid_x and ball_rect.left <= grid_x + grid_w and
                ball_rect.bottom >= grid_y and ball_rect.top <= grid_y + grid_h):
                
                # Calcular la celda colisionada (0-8)
                col = int((ball_rect.centerx - grid_x) // 60)
                row = int((ball_rect.centery - grid_y) // 60)
                
                if 0 <= col < 3 and 0 <= row < 3:
                    idx = row * 3 + col
                    # Solo marcar si la celda está vacía y el último en golpear es un jugador
                    if self.game.tictactoe_board[idx] is None and self.game.last_hitter in [1, 2]:
                        self.game.tictactoe_board[idx] = self.game.last_hitter
                        self.game.audio.play('hit')  # Sonido de confirmación al marcar la celda
                        self.game._check_tictactoe_win()

    def _apply_planet_gravity(self, ball, dt):
        spd = math.sqrt(ball.vx**2 + ball.vy**2)
        for p_idx, pos in enumerate([self.game.planet1_pos, self.game.planet2_pos]):
            if (p_idx == 0 and self.game.planet1_alive) or (p_idx == 1 and self.game.planet2_alive):
                dx, dy = pos[0]-ball.rect.centerx, pos[1]-ball.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                rad = self.game.gravity_radius_options[self.game.gravity_radius_idx]
                force = self.game.gravity_force_options[self.game.gravity_force_idx]
                if self.game.planet_radius < dist < rad:
                    f = (1.0 - (dist / rad)) * force
                    ball.vx += (dx/dist)*f*dt*60; ball.vy += (dy/dist)*f*dt*60
        # Mantener velocidad constante (la gravedad solo curva)
        new_spd = math.sqrt(ball.vx**2 + ball.vy**2)
        if new_spd > 0: ball.vx = (ball.vx/new_spd)*spd; ball.vy = (ball.vy/new_spd)*spd

    def _check_planet_collisions(self, ball):
        for p_idx, planet_pos in enumerate([self.game.planet1_pos, self.game.planet2_pos]):
            is_alive = self.game.planet1_alive if p_idx == 0 else self.game.planet2_alive
            if not is_alive: continue
            dx, dy = ball.rect.centerx - planet_pos[0], ball.rect.centery - planet_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < self.game.planet_radius + ball.rect.width / 2:
                # Protección contra división por cero
                if dist == 0: dist = 0.1; dx = 0.1
                nx, ny = dx/dist, dy/dist
                dot = ball.vx * nx + ball.vy * ny
                ball.vx -= 2 * dot * nx; ball.vy -= 2 * dot * ny
                overlap = (self.game.planet_radius + ball.rect.width / 2) - dist
                ball.rect.centerx += nx * (overlap + 2); ball.rect.centery += ny * (overlap + 2)
                ball.x_float = float(ball.rect.x); self.game.audio.play('pop')
                if self.game.destructible_planets_enabled:
                    self.game._handle_planet_damage(p_idx, planet_pos)

    def _check_portal_collisions(self, ball):
        colliding_blue = ball.rect.colliderect(self.game.portal_blue_rect)
        colliding_orange = ball.rect.colliderect(self.game.portal_orange_rect)
        colliding_red = self.game.more_portals_enabled and ball.rect.colliderect(self.game.portal_red_rect)
        colliding_green = self.game.more_portals_enabled and ball.rect.colliderect(self.game.portal_green_rect)
        
        # Resetear ID si no toca nada para permitir re-entrada
        if not colliding_blue and not colliding_orange and not colliding_red and not colliding_green:
            ball.last_portal_id = None
            return

        # Si ya estamos en cooldown de ese portal, no hacer nada
        if ball.last_portal_id: return

        if colliding_blue:
            self._teleport_ball(ball, self.game.portal_blue_rect, self.game.portal_orange_rect, "orange", BLUE)
        elif colliding_orange:
            self._teleport_ball(ball, self.game.portal_orange_rect, self.game.portal_blue_rect, "blue", ORANGE)
        elif colliding_red:
            self._teleport_ball(ball, self.game.portal_red_rect, self.game.portal_green_rect, "green", RED)
        elif colliding_green:
            self._teleport_ball(ball, self.game.portal_green_rect, self.game.portal_red_rect, "red", GREEN)

    def _teleport_ball(self, ball, from_rect, to_rect, target_id, color):
        self.game.audio.play('ghost') # Sonido de portal
        self.game.vfx.explosion(from_rect.centerx, from_rect.centery, color)
        
        # Teletransporte con lógica de portales (Vertical vs Horizontal)
        if self.game.portals_vertical:
            ball.y_float = float(to_rect.y + (ball.y_float - from_rect.y))
            if to_rect.x < SCREEN_WIDTH // 2: ball.x_float = to_rect.right + 2
            else: ball.x_float = to_rect.left - ball.rect.width - 2
            ball.vx *= 1.005 # Pequeño impulso de velocidad
        else:
            ball.x_float = float(to_rect.x + (ball.x_float - from_rect.x))
            if to_rect.y < SCREEN_HEIGHT // 2: ball.y_float = to_rect.bottom + 2
            else: ball.y_float = to_rect.top - ball.rect.height - 2
            ball.vy *= -1.005 # Invertir y dar impulso
        
        ball.last_portal_id = target_id
        ball.rect.x, ball.rect.y = int(ball.x_float), int(ball.y_float)
        self.game.vfx.explosion(ball.rect.centerx, ball.rect.centery, color)

    def _check_world_collisions(self, ball):
        is_main = (ball == self.game.balls[0])
        
        # X2 Item
        if is_main and self.game.is_x2_item_active and ball.rect.colliderect(self.game.x2_item_rect):
            self.game.is_x2_item_active = False; self.game.ball_is_x2 = True; ball.color = GOLD; self.game.audio.play('x2')
            self.game.vfx.burst(self.game.x2_item_rect.centerx, self.game.x2_item_rect.centery, GOLD)

        # Relojes
        if is_main and self.game.hourglass_rect and ball.rect.colliderect(self.game.hourglass_rect):
            self.game._handle_watch_capture()

        # Goles
        if ball.rect.right < 0:
            self._handle_goal(ball, True)
        elif ball.rect.left > SCREEN_WIDTH:
            self._handle_goal(ball, False)

        # Paletas (Detección de colisión)
        if ball.is_bullet and ball.bullet_immunity <= 0:
            if ball.rect.colliderect(self.game.paddle1.rect):
                self.game.handle_paddle_collision(self.game.paddle1, 1, ball); return
            if ball.rect.colliderect(self.game.paddle2.rect):
                self.game.handle_paddle_collision(self.game.paddle2, -1, ball); return

        if ball.vx < 0 and ball.rect.colliderect(self.game.paddle1.rect):
            if ball.is_ghost and ball.ghost_owner == 2:
                self.game.audio.play('hit'); self.game.balls.remove(ball)
            else: self.game.handle_paddle_collision(self.game.paddle1, 1, ball)
        elif ball.vx > 0 and ball.rect.colliderect(self.game.paddle2.rect):
            if ball.is_ghost and ball.ghost_owner == 1:
                self.game.audio.play('hit'); self.game.balls.remove(ball)
            else: self.game.handle_paddle_collision(self.game.paddle2, -1, ball)

    def _handle_goal(self, ball, is_left):
        if ball.is_bullet:
            if ball in self.game.balls: self.game.balls.remove(ball)
        elif ball.is_ghost:
            owner_needed = 2 if is_left else 1
            if ball.ghost_owner == owner_needed: self.game.goal_scored(owner_needed)
            if ball in self.game.balls: self.game.balls.remove(ball)
        elif ball.is_orange: self.game._handle_orange_bounce(is_left, ball)
        elif (self.game.paddle1.has_extra_life if is_left else self.game.paddle2.has_extra_life):
            self.game._handle_extra_life_save(is_left, ball)
        else:
            self.game.goal_scored(2 if is_left else 1)

    def apply_magnet_force(self, p, dt, ball):
        spd = math.sqrt(ball.vx**2 + ball.vy**2)
        incoming = (p == self.game.paddle1 and ball.vx < 0) or (p == self.game.paddle2 and ball.vx > 0)
        dx, dy = p.rect.centerx - ball.rect.centerx, p.rect.centery - ball.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            target_vx, target_vy = (dx/dist)*spd, (dy/dist)*spd
            if incoming: ball.vx += (target_vx - ball.vx)*0.2*dt*60; ball.vy += (target_vy - ball.vy)*0.2*dt*60
            else: ball.vy += (target_vy - ball.vy)*0.1*dt*60
        new_spd = math.sqrt(ball.vx**2 + ball.vy**2)
        if new_spd > 0: ball.vx = (ball.vx/new_spd)*spd; ball.vy = (ball.vy/new_spd)*spd
        if not ball.is_orange: ball.color = (100, 200, 255)
