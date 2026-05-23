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
    # Al reiniciar la partida el estado pasa a saque (STATE_SERVE)
    assert game.state == STATE_SERVE

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

def test_endless_modifier_progression_rules(game):
    # Validar que la velocidad del ratón sea la Normal por defecto (índice 1)
    assert game.mouse_speed_idx == 1

    # Definir los IDs válidos de EXTRAS (excluyendo start_x2 y experimental_golden_goal)
    extras_ids = {
        "orange_watch", "tictactoe", "magnet_power", "ghost_power", "ghost_identical", 
        "gum_power", "floating_planets", "destructible_planets", 
        "portals", "portals_vertical", "more_portals", "add_mouse", "revolver", 
        "sleeping_power", "cloudy_day", "rainy_day", "lightning"
    }

    # Nivel 1: El modificador debe pertenecer estrictamente a EXTRAS
    game.endless_active = True
    game.endless_level = 1
    game.endless_active_modifiers = []
    game.generate_next_endless_modifier()
    
    assert len(game.endless_active_modifiers) == 1
    mod = game.endless_active_modifiers[0]
    assert mod["id"] in extras_ids
    assert not mod["id"].startswith("remove_")
    assert mod["id"] != "mouse_speed"
    assert mod["id"] != "start_x2"
    assert mod["id"] != "experimental_golden_goal"

    # Nivel 2: No debe permitirse ningún modificador de "Remove..." ni start_x2 ni experimental_golden_goal
    game.endless_level = 2
    game.endless_active_modifiers = []
    # Ejecutamos 20 simulaciones para estar seguros de que en ningún caso salen modificadores prohibidos
    for _ in range(20):
        game.endless_active_modifiers = []
        game.generate_next_endless_modifier()
        for active_mod in game.endless_active_modifiers:
            assert not active_mod["id"].startswith("remove_")
            assert active_mod["id"] != "mouse_speed"
            assert active_mod["id"] != "start_x2"
            assert active_mod["id"] != "experimental_golden_goal"


def test_weather_reset_on_game_restart(game):
    # Simular que el clima estaba activo con nubes, gotas, temporizadores y relámpago
    from entities import Cloud
    game.clouds = [Cloud(100, 100, 1, 1.0, 1.0)]
    game.rain_drops = [{"x": 10, "y": 20, "speed": 5, "length": 10}]
    game.rain_timer = 15.5
    game.cloud_spawn_timer = 5
    game.lightning_active = True
    game.lightning_flash_timer = 0.2
    game.lightning_timer = 4.0
    game.rain_sound_playing = True

    # Ejecutar reinicio del juego
    game.reset_game(skip_announcement=True)

    # Verificar que todas las variables dinámicas de clima se han restablecido por completo
    assert len(game.clouds) == 0
    assert len(game.rain_drops) == 0
    assert game.rain_timer == 0.0
    assert game.cloud_spawn_timer == 0
    assert not game.lightning_active
    assert game.lightning_flash_timer == 0.0
    assert game.lightning_timer == 0.0
    assert not game.rain_sound_playing

