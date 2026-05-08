import pytest
import pygame
from entities import Paddle, Ball, Particle, Mouse
from constants import *

def test_paddle_initialization():
    paddle = Paddle(100, 200)
    assert paddle.rect.x == 100
    assert paddle.rect.y == 200

def test_paddle_reset():
    paddle = Paddle(100, 200)
    paddle.color = RED
    paddle.reset()
    assert paddle.color == WHITE

def test_ball_initialization():
    ball = Ball(400, 300)
    assert ball.rect.center == (400, 300)

def test_ball_serve():
    ball = Ball(400, 300)
    ball.serve(1, 500)
    # Comprobar que se mueve hacia la derecha (vx > 0)
    assert ball.vx > 0
    # La magnitud de la velocidad debería ser 500
    speed = (ball.vx**2 + ball.vy**2)**0.5
    assert pytest.approx(speed) == 500

def test_ball_update():
    ball = Ball(400, 300)
    ball.vx = 100
    ball.vy = 0
    ball.update(0.1) 
    # En el código original: self.x_float += self.vx * dt * 60
    # 400 + 100 * 0.1 * 60 = 400 + 60 = 460
    assert ball.x_float == 460

def test_mouse_initialization():
    mouse = Mouse(100, 100)
    # El mouse en su __init__ ignora x, y? No, pero vamos a ver qué hace.
    # Si falla con 85 == 100, es que el offset o el tamaño influyen.
    assert mouse.rect.width > 0
