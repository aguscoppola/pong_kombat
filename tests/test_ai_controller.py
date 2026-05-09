import pytest
import pygame
from game_engine import Game
from entities import Ball
from constants import *

@pytest.fixture
def game():
    # Inicializar pygame en modo headless para los tests
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    return Game()

def test_ai_follows_ball(game):
    # En modo AI, la paleta 2 debe seguir a la pelota
    game.is_ai_mode = True
    ball = Ball(SCREEN_WIDTH // 2, 100) # Pelota arriba
    game.balls = [ball]
    
    # Paleta 2 empieza en el centro
    game.paddle2.rect.centery = SCREEN_HEIGHT // 2
    
    # Actualizar IA
    game.ai_controller.update(0.1) # 100ms
    
    # La paleta 2 debería haberse movido hacia arriba (y menor)
    assert game.paddle2.rect.centery < SCREEN_HEIGHT // 2

def test_ai_evades_yellow_bullet(game):
    game.is_ai_mode = True
    # Bala amarilla viniendo hacia la IA por el centro
    bullet = Ball(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
    bullet.is_bullet = True
    bullet.vx = 500
    game.balls = [bullet]
    
    # Paleta 2 en el centro
    game.paddle2.rect.centery = SCREEN_HEIGHT // 2
    
    # Actualizar IA
    game.ai_controller.update(0.1)
    
    # La paleta 2 debería haberse movido para esquivar (arriba o abajo)
    assert game.paddle2.rect.centery != SCREEN_HEIGHT // 2

def test_ai_revolver_aiming(game):
    game.is_ai_mode = True
    game.paddle2.power_active = POWER_REVOLVER
    
    # Paleta 1 está arriba
    game.paddle1.rect.centery = 100
    # Paleta 2 está en el centro
    game.paddle2.rect.centery = SCREEN_HEIGHT // 2
    
    # Actualizar IA
    game.ai_controller.update(0.1)
    
    # La IA con revólver debería apuntar a la paleta 1 (moverse hacia arriba)
    assert game.paddle2.rect.centery < SCREEN_HEIGHT // 2
