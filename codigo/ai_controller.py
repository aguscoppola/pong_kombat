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
        # Filtrar pelotas: Ignorar las propias pelotas fantasmas siempre
        # Priorizar pelotas reales sobre las fantasmas del oponente
        real_balls = [b for b in self.game.balls if not b.is_ghost]
        opponent_ghosts = [b for b in self.game.balls if b.is_ghost and b.ghost_owner == 1]
        
        valid_balls = real_balls + opponent_ghosts
        
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
            # Distancia de reacción
            if threat.rect.right > SCREEN_WIDTH * 0.05: # Reaccionar un poco antes
                # AMENAZAS CRÍTICAS: Balas, Naranja y Sueño (Violeta)
                is_critical = getattr(threat, "is_bullet", False) or getattr(threat, "is_orange", False) or getattr(threat, "is_sleep", False)
                
                # Comprobar urgencia de la pelota
                ball_urgent = False
                if valid_balls:
                    ball_dist_x = abs(target_ball.rect.centerx - p2.rect.centerx)
                    # Si la amenaza es crítica, prioridad total a esquivar
                    # Solo ignoramos la esquiva si la pelota está CASI entrando y la amenaza está lejos
                    threat_dist_x = abs(threat.rect.centerx - p2.rect.centerx)
                    if is_critical:
                        # Si es naranja, reaccionar con más margen de seguridad
                        is_orange = getattr(threat, "is_orange", False)
                        safety_margin = 250 if is_orange else 200
                        
                        if ball_dist_x < 30 and threat_dist_x > safety_margin:
                            ball_urgent = True
                        else:
                            ball_urgent = False
                    else:
                        if target_ball.vx > 0 and ball_dist_x < 180:
                            ball_urgent = True
                
                # Esquivar si está en curso de colisión
                if not ball_urgent:
                    padding = 60 # Más margen de seguridad (v0.6.0 Fix)
                    if abs(p2.rect.centery - threat.rect.centery) < (p2.rect.height // 2 + padding):
                        # Moverse al lado contrario de la amenaza con más fuerza
                        if threat.rect.centery < p2.rect.centery:
                            dodge_offset = 120 # Esquiva más amplia
                        else:
                            dodge_offset = -120
                        
                        # Si es una bala o naranja, forzar alejarse aún más si está muy cerca
                        if is_critical and threat_dist_x < 250:
                            if threat.rect.centery < p2.rect.centery:
                                dodge_offset = 150
                            else:
                                dodge_offset = -150

        # 3. Lógica de Ataque y Apuntar
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
        
        # GUM (Chicle)
        if p2.power_active == POWER_GUM:
            if p2.is_stuck:
                # Soltar si estamos alineados para meter gol o tras un tiempo
                if abs(p2.rect.centery - SCREEN_HEIGHT // 2) < 100 or random.random() < 0.05:
                    self.game.activate_paddle_power(p2, 2)
            elif p2.gum_charges > 0:
                # Disparar proyectil si el jugador está alineado
                if abs(p2.rect.centery - p1.rect.centery) < 100 and random.random() < 0.03:
                    self.game.activate_paddle_power(p2, 2)
        
        # REVOLVER (Disparar)
        if p2.power_active == POWER_REVOLVER:
            if p2.revolver_shots_left > 0:
                # Disparar si el jugador 1 está cerca de la línea horizontal
                if abs(p2.rect.centery - p1.rect.centery) < 60:
                    if random.random() < 0.08: # Ráfagas aleatorias
                        self.game.activate_paddle_power(p2, 2)
            else:
                p2.power_active = POWER_NONE

        # Activar poder si está guardado (Estrategia)
        if p2.power_stored != POWER_NONE:
            # Activar chicle si la pelota viene de frente
            if p2.power_stored == POWER_GUM and valid_balls and target_ball.vx > 0:
                if abs(p2.rect.centery - target_ball.rect.centery) < 50:
                    self.game.activate_paddle_power(p2, 2)
            # Activar revólver inmediatamente para tenerlo listo
            elif p2.power_stored == POWER_REVOLVER:
                self.game.activate_paddle_power(p2, 2)

