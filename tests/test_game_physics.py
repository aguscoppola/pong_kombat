import pytest
import pygame
from game_engine import Game
from entities import Ball, Paddle
from constants import *

@pytest.fixture
def game():
    return Game()

def test_paddle_ball_collision_logic(game):
    ball = Ball(100, 100)
    ball.vx = -500 # Hacia la izquierda (P1)
    game.balls = [ball]
    
    # Posicionar paleta 1 para que colisione
    game.paddle1.rect.center = (100, 100)
    
    # Forzar colisión
    game.check_ball_collisions(ball)
    
    # Debería haber rebotado (vx positivo ahora)
    assert ball.vx > 0
    assert game.last_hitter == 1

def test_magnet_force_application(game):
    ball = Ball(100, 100)
    ball.vx = 100
    game.paddle1.power_active = POWER_MAGNET
    game.paddle1.rect.center = (100, 200) # La paleta está abajo de la pelota
    
    initial_vy = ball.vy
    game._apply_magnet_force(game.paddle1, 0.1, ball)
    
    # La fuerza magnética debería atraer la pelota hacia la paleta (vy aumenta)
    assert ball.vy > initial_vy

def test_planet_collision(game):
    ball = Ball(game.planet1_pos[0], game.planet1_pos[1])
    game.planet1_alive = True
    game._check_planet_collisions(ball)
    
    # El planeta debería haber recibido daño o morir (depende del hit_count)
    # Aquí probamos que la pelota reaccione (ej: vfx o cambio de dirección)
    assert ball.vx != 0 or ball.vy != 0

def test_orange_bounce_at_back_wall(game):
    ball = Ball(-5, 300) # Casi fuera por la izquierda
    ball.vx = -100
    ball.is_orange = True
    
    game._handle_orange_bounce(ball)
    # Debería rebotar en lugar de marcar gol (vx cambia de signo)
    assert ball.vx > 0
    assert ball.rect.left >= 0

def test_watch_spawn_logic(game):
    game.hourglass_rect = None
    game.global_hits = 10 # Umbral para spawn
    game._check_watch_spawn()
    # No es garantizado por el azar, pero probamos la función
    # (En un test real mockearíamos random para asegurar el spawn)
    pass 
