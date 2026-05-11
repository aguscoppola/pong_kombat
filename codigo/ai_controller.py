import random
import math
from constants import *

class AIController:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        if not self.game.is_ai_mode:
            return
        p2 = self.game.paddle2
        p1 = self.game.paddle1

        # 1. Prioridad: Determinar objetivo de la pelota (Seguir / Anticipar)
        target_y = None
        valid_balls = [b for b in self.game.balls if not (b.is_ghost and b.ghost_owner == 2)]
        if valid_balls:
            target_ball = min(valid_balls, key=lambda b: abs(b.rect.centerx - p2.rect.centerx))
            target_y = target_ball.rect.centery
            # Anticipación de portales
            if self.game.portals_enabled:
                portal_pairs = [(self.game.portal_blue_rect, self.game.portal_orange_rect), (self.game.portal_red_rect, self.game.portal_green_rect) if self.game.more_portals_enabled else (None, None)]
                for r1, r2 in portal_pairs:
                    if r1 and r2:
                        if r1.inflate(20, 20).colliderect(target_ball.rect): target_y = r2.centery; break
                        elif r2.inflate(20, 20).colliderect(target_ball.rect): target_y = r1.centery; break

        # 2. Prioridad: Esquivar proyectiles
        dodge_offset = 0
        # Amenazas letales (Revólver / Naranja) e inmovilizantes (v0.6.0)
        threats = [b for b in self.game.balls if (b.is_bullet or b.is_orange) and b.vx > 0]
        threats += [sp for sp in self.game.sleep_projectiles if sp.vx > 0]
        
        if threats:
            threat = min(threats, key=lambda b: abs(b.rect.centerx - p2.rect.centerx))
            # Distancia de reacción (v0.6.0 Fix)
            if threat.rect.right > SCREEN_WIDTH * 0.1:
                is_lethal = getattr(threat, "is_bullet", False) or getattr(threat, "is_orange", False)
                
                # Comprobar urgencia de la pelota
                ball_urgent = False
                if valid_balls:
                    ball_dist_x = abs(target_ball.rect.centerx - p2.rect.centerx)
                    # Si la amenaza es letal, solo ignoramos la esquiva si la pelota está ENCIMA de la paleta
                    limit = 80 if is_lethal else 220
                    if target_ball.vx > 0 and ball_dist_x < limit:
                        ball_urgent = True
                
                # Esquivar si está en curso de colisión
                if not ball_urgent:
                    padding = 30
                    if abs(p2.rect.centery - threat.rect.centery) < (p2.rect.height // 2 + padding):
                        # Moverse al lado contrario de la amenaza
                        if threat.rect.centery < p2.rect.centery:
                            dodge_offset = 70 # Abajo
                        else:
                            dodge_offset = -70 # Arriba

        # 3. Lógica de Ataque y Apuntar (v0.6.0 Fix)
        if p2.power_active == POWER_SLEEP:
            # Si no hay pelota viniendo, apuntar activamente al centro del jugador
            if not valid_balls or target_ball.vx < 0:
                target_y = p1.rect.centery

        # 4. Movimiento final
        final_y = target_y if target_y is not None else SCREEN_HEIGHT // 2
        final_y += dodge_offset
        
        if not p2.is_stuck:
            if final_y < p2.rect.centery - 10: p2.move(-1, dt, PADDLE_SPEED)
            elif final_y > p2.rect.centery + 10: p2.move(1, dt, PADDLE_SPEED)

        # 5. Lógica de activación de poderes
        # SLEEP
        if p2.power_active == POWER_SLEEP:
            if abs(p2.rect.centery - p1.rect.centery) < 40:
                if random.random() < 0.08: self.game.activate_paddle_power(p2, 2)
            elif p1.power_stored in [POWER_FIREBALL, POWER_ORANGE] and random.random() < 0.02:
                self.game.activate_paddle_power(p2, 2)
        
        # Otros poderes (Magneto, Chicle, Revolver) - Mantener lógica existente simplificada
        if p2.power_active == POWER_MAGNET and valid_balls and target_ball.vx < 0:
            if random.random() < 0.05: pass # La paleta ya se mueve por inercia en Magnet
            
        if p2.power_active == POWER_GUM and p2.is_stuck:
            if random.random() < 0.05: self.game.activate_paddle_power(p2, 2)
            
        if p2.power_active == POWER_REVOLVER:
            if valid_balls and target_ball.vx > 0 and abs(p2.rect.centery - p1.rect.centery) < 100:
                if random.random() < 0.05: self.game.activate_paddle_power(p2, 2)

