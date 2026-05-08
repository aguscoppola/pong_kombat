import pytest
import pygame
from game_engine import Game
from constants import *

@pytest.fixture
def game():
    return Game()

def test_activate_revolver_power(game):
    game.paddle1.power_stored = POWER_REVOLVER
    game.activate_paddle_power(game.paddle1, 1)
    
    assert game.paddle1.power_active == POWER_REVOLVER
    assert game.paddle1.revolver_shots_left == 3
    assert game.paddle1.power_stored == POWER_NONE

def test_shoot_revolver(game):
    game.paddle1.power_active = POWER_REVOLVER
    game.paddle1.revolver_shots_left = 3
    
    game.activate_paddle_power(game.paddle1, 1)
    
    assert game.paddle1.revolver_shots_left == 2
    # Debería haber una bala (pelota amarilla) en la lista de pelotas
    assert any(b.is_bullet for b in game.balls)

def test_ghost_power_spawns_ball(game):
    game.paddle1.power_stored = POWER_GHOST
    initial_balls = len(game.balls)
    game.activate_paddle_power(game.paddle1, 1)
    
    assert len(game.balls) == initial_balls + 1
    assert game.balls[-1].is_ghost == True

def test_watch_capture_effects(game):
    # Capturar reloj tipo 0 (Velocidad)
    game.hourglass_type = 0
    game._handle_watch_capture(game.paddle1)
    assert game.paddle1.speed_multiplier > 1.0
    
    # Capturar reloj tipo 3 (Invertir controles rival)
    game.hourglass_type = 3
    game._handle_watch_capture(game.paddle1)
    assert game.paddle2.controls_inverted == True

def test_reset_ball_visuals(game):
    ball = game.balls[0] if game.balls else None
    if not ball: 
        from entities import Ball
        ball = Ball(100, 100)
    
    ball.is_orange = True
    ball.color = ORANGE
    game.reset_ball_visuals(ball)
    assert ball.is_orange == False
    assert ball.color == WHITE
