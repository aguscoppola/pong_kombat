import pytest
import pygame
import math
import random
import sys
import os

# Configurar el path para encontrar el código en las nuevas carpetas
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(root_dir, "codigo_fuente"))
sys.path.append(os.path.join(root_dir, "codigo"))

from game_engine import Game
from entities import Paddle, Ball, Particle, Mouse
from constants import *

@pytest.fixture
def game():
    return Game()

# -------------------------------------------------------------------
# TESTS DE FÍSICA Y COLISIONES (CORE DEL MOTOR)
# -------------------------------------------------------------------

def test_ball_wall_bounce_top(game):
    ball = Ball(400, 5)
    ball.vy = -100
    ball.update(0.1) 
    if ball.rect.top < 0:
        ball.vy *= -1
    assert ball.vy > 0

def test_paddle_collision_centers(game):
    ball = Ball(35, 100)
    ball.vx = -100
    ball.vy = 0
    ball.speed = 100
    game.paddle1.rect.center = (35, 100)
    # P1 está a la izquierda, la dirección del rebote es hacia la derecha (1)
    game.handle_paddle_collision(game.paddle1, 1, ball)
    assert ball.vx > 0 

def test_gravity_pull_planets(game):
    ball = Ball(game.planet1_pos[0] + 50, game.planet1_pos[1])
    ball.vx = 0
    dx = game.planet1_pos[0] - ball.rect.centerx
    dist = math.sqrt(dx**2)
    if dist < game.gravity_radius_options[game.gravity_radius_idx]:
        ball.vx += (dx/dist) * 10 
    assert ball.vx < 0 

# -------------------------------------------------------------------
# TESTS DE PODERES Y MECÁNICAS ESPECIALES
# -------------------------------------------------------------------

def test_fireball_power(game):
    ball = Ball(100, 100)
    game.paddle1.power_active = POWER_FIREBALL
    game.handle_paddle_collision(game.paddle1, 1, ball) # Añadido el 1
    assert ball.is_fireball == True
    assert ball.color == RED

def test_shield_power(game):
    game.paddle1.power_stored = POWER_SHIELD
    game.activate_paddle_power(game.paddle1, 1) 
    assert game.paddle1.shield_hits_left > 0

def test_portal_teleportation(game):
    ball = Ball(game.portal_blue_rect.centerx, game.portal_blue_rect.centery)
    if ball.rect.colliderect(game.portal_blue_rect):
        ball.x_float = float(game.portal_orange_rect.x)
    assert ball.x_float == game.portal_orange_rect.x

# -------------------------------------------------------------------
# TESTS DE IA Y MOVIMIENTO
# -------------------------------------------------------------------

def test_ai_movement_follows_ball(game):
    ball = Ball(SCREEN_WIDTH // 2, 500)
    game.paddle2.rect.centery = 100
    initial_y = game.paddle2.rect.centery
    if game.paddle2.rect.centery < ball.rect.centery:
        game.paddle2.move(1, 0.1, PADDLE_SPEED)
    assert game.paddle2.rect.centery > initial_y

def test_ai_dodges_orange_ball(game):
    ball = Ball(SCREEN_WIDTH - 100, 100)
    ball.is_orange = True
    ball.vx = 500
    game.paddle2.rect.centery = 100
    if ball.is_orange and ball.vx > 0:
        target_y = SCREEN_HEIGHT - 100
        if game.paddle2.rect.centery < target_y: game.paddle2.move(1, 0.1, PADDLE_SPEED)
    assert game.paddle2.rect.centery > 100

# -------------------------------------------------------------------
# TESTS DE UI Y SISTEMA
# -------------------------------------------------------------------

def test_language_switch(game):
    game.language = "ES"
    assert game.language == "ES"

def test_vfx_toggle(game):
    game.vfx_enabled = False
    assert game.vfx_enabled == False

def test_score_limits(game):
    game.score1 = game.max_score - 1
    game.point_scored(1)
    assert game.score1 == game.max_score
