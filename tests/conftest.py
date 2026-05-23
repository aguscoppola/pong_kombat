import pytest
import pygame
import sys
import os
from unittest.mock import MagicMock

# Configurar el path para los tests
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(root_dir, "codigo_fuente"))
sys.path.append(os.path.join(root_dir, "codigo"))

@pytest.fixture(autouse=True)
def mock_pygame():
    """Mockea todas las llamadas a Pygame para que los tests no necesiten ventana."""
    pygame.display.init = MagicMock()
    pygame.display.set_mode = MagicMock(return_value=MagicMock())
    pygame.display.flip = MagicMock()
    pygame.display.update = MagicMock()
    pygame.mixer.init = MagicMock()
    pygame.mixer.Sound = MagicMock()
    pygame.font.init = MagicMock()
    
    mock_font = MagicMock()
    mock_font.render = MagicMock(return_value=pygame.Surface((10,10)))
    mock_font.size = MagicMock(return_value=(50, 10))
    pygame.font.SysFont = MagicMock(return_value=mock_font)
    pygame.font.Font = MagicMock(return_value=mock_font)
    
    pygame.image.load = MagicMock(return_value=pygame.Surface((10,10)))
    pygame.mixer.pre_init = MagicMock()
    # Mockear el clock para controlar el tiempo en los tests
    pygame.time.Clock = MagicMock()
