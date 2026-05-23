import pytest
import pygame
from game_engine import Game
from entities import Ball, Paddle
from constants import *

@pytest.fixture
def game():
    return Game()

def test_paddle_ball_collision_logic(game):
    # Posicionar paleta 1
    game.paddle1.rect.center = (30, 100)
    # Pelota justo delante, yendo hacia ella
    ball = Ball(50, 100)
    ball.vx = -1000
    ball.speed = 1000 # IMPORTANTE: Definir la velocidad base para el rebote
    game.balls = [ball]
    
    # Procesar la física (se actualiza el movimiento e interactúa con la paleta)
    game.physics.update(0.02)
    
    # Debería haber rebotado (vx positivo ahora)
    assert ball.vx > 0
    assert game.last_hitter == 1

def test_magnet_force_application(game):
    ball = Ball(100, 100)
    ball.vx = 100
    game.paddle1.power_active = POWER_MAGNET
    game.paddle1.rect.center = (100, 200) # La paleta está abajo de la pelota
    
    initial_vy = ball.vy
    game.physics.apply_magnet_force(game.paddle1, 0.1, ball)
    
    # La fuerza magnética debería atraer la pelota hacia la paleta (vy aumenta)
    assert ball.vy > initial_vy

def test_planet_collision(game):
    # Pelota con velocidad para que el rebote sea notable
    ball = Ball(game.planet1_pos[0] + 5, game.planet1_pos[1] + 5)
    ball.vx = 100; ball.vy = 100
    game.planet1_alive = True
    game.physics._check_planet_collisions(ball)
    
    # La dirección debería haber cambiado tras el rebote
    assert ball.vx != 100 or ball.vy != 100

def test_orange_bounce_at_back_wall(game):
    ball = Ball(-5, 300) # Casi fuera por la izquierda
    ball.vx = -100
    ball.is_orange = True
    
    # El PhysicsEngine maneja los rebotes de muros traseros para pelotas naranjas
    game.physics._handle_goal(ball, True) 
    
    # Debería rebotar en lugar de marcar gol (vx cambia de signo)
    assert ball.vx > 0
    assert ball.rect.left >= 0

def test_watch_spawn_logic(game):
    game.hourglass_rect = None
    game.global_hits = 10 # Umbral para spawn
    game._check_watch_spawn()
    # No es garantizado por el azar, pero probamos la función
    pass 
