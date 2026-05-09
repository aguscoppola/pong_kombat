import pytest
import pygame
from game_engine import Game
from menu_manager import MenuManager
from constants import *

@pytest.fixture
def game():
    # Inicializar pygame para evitar errores de fuentes
    pygame.init()
    # Crear una superficie de display dummy
    pygame.display.set_mode((800, 600), pygame.HIDDEN)
    g = Game()
    yield g
    pygame.quit()

def test_menu_manager_integration(game):
    """Verifica que el MenuManager está correctamente inyectado."""
    assert hasattr(game, 'menus')
    assert isinstance(game.menus, MenuManager)

def test_menu_draw_call(game):
    """Verifica que el método draw() no crashea."""
    try:
        game.draw()
    except Exception as e:
        pytest.fail(f"game.draw() crasheó: {e}")
