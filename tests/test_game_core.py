import pytest
import pygame
from game_engine import Game
from entities import Paddle, Ball
from constants import *

@pytest.fixture
def game():
    return Game()

def test_game_initial_state(game):
    assert game.state == STATE_MAIN_MENU
    assert game.score1 == 0
    assert game.score2 == 0

def test_game_reset(game):
    game.score1 = 5
    game.score2 = 3
    game.reset_game()
    assert game.score1 == 0
    assert game.score2 == 0
    # En el original, reset_game pone el estado en STATE_MAIN_MENU
    assert game.state == STATE_MAIN_MENU

def test_point_scored_basic(game):
    game.score1 = 0
    game.point_scored(1)
    assert game.score1 == 1

def test_game_init_fonts(game):
    # Probar que las fuentes se inicializaron (no son None)
    assert game.font is not None
    assert game.large_font is not None

def test_game_init_entities(game):
    assert isinstance(game.paddle1, Paddle)
    assert isinstance(game.paddle2, Paddle)
    assert len(game.balls) > 0
