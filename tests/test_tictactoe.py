import pytest
import pygame
from game_engine import Game
from constants import *

@pytest.fixture
def game():
    return Game()

def test_tictactoe_initial_state(game):
    # Por defecto, Ta-Te-Ti empieza deshabilitado y vacío
    assert game.tictactoe_enabled is False
    assert len(game.tictactoe_board) == 9
    assert all(x is None for x in game.tictactoe_board)
    assert game.tictactoe_winner is None
    assert game.tictactoe_win_line is None
    assert game.tictactoe_win_timer == 0.0

def test_reset_tictactoe(game):
    # Rellenamos el tablero
    game.tictactoe_board = [1, 2, 1, 2, 1, 2, 1, 2, 1]
    game.tictactoe_winner = 1
    game.tictactoe_win_line = [0, 4, 8]
    game.tictactoe_win_timer = 0.8
    
    # Reseteamos
    game.reset_tictactoe()
    assert all(x is None for x in game.tictactoe_board)
    assert game.tictactoe_winner is None
    assert game.tictactoe_win_line is None
    assert game.tictactoe_win_timer == 0.0

def test_check_win_horizontal(game):
    game.tictactoe_enabled = True
    # Fila superior
    game.tictactoe_board[0] = 1
    game.tictactoe_board[1] = 1
    game.tictactoe_board[2] = 1
    
    game._check_tictactoe_win()
    assert game.tictactoe_winner == 1
    assert game.tictactoe_win_line == [0, 1, 2]
    assert game.tictactoe_win_timer == 0.8

def test_check_win_diagonal(game):
    game.tictactoe_enabled = True
    # Diagonal principal para J2
    game.tictactoe_board[0] = 2
    game.tictactoe_board[4] = 2
    game.tictactoe_board[8] = 2
    
    game._check_tictactoe_win()
    assert game.tictactoe_winner == 2
    assert game.tictactoe_win_line == [0, 4, 8]
    assert game.tictactoe_win_timer == 0.8

def test_ball_grid_collision(game):
    from physics_engine import PhysicsEngine
    physics = PhysicsEngine(game)
    
    game.tictactoe_enabled = True
    game.last_hitter = 1  # Player 1 golpeó la pelota
    
    # Colocar la pelota en la celda central (fila 1, columna 1)
    # Rango de celda central: x de 370 a 430, y de 270 a 330
    ball = game.balls[0]
    ball.rect.center = (400, 300)
    
    physics._check_tictactoe_collisions(ball)
    
    # Debería haber marcado la celda central (índice 4) con el símbolo de J1
    assert game.tictactoe_board[4] == 1
