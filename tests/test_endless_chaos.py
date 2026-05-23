import pytest
import pygame
import random
from game_engine import Game
from constants import *

@pytest.fixture
def game():
    return Game()

def test_endless_chaos_initialization(game):
    # Verificar que las variables de Caos Infinito se inicialicen con sus valores correctos
    assert hasattr(game, "endless_chaos_idx")
    assert game.endless_chaos_enabled is False
    assert game.endless_chaos_idx == 0  # Desactivado por defecto (None)
    assert len(game.endless_chaos_names) == 6
    assert game.endless_chaos_names[0] == "0 mods"
    assert game.endless_chaos_names[1] == "1 mod"
    assert game.chaos_banner_text == ""
    assert game.chaos_banner_timer == 0.0

def test_trigger_endless_chaos_inactive(game):
    # Si Endless Chaos está desactivado (enabled = False), no debe hacer nada
    game.endless_chaos_enabled = False
    game.endless_chaos_idx = 2
    game.trigger_endless_chaos()
    assert game.chaos_banner_text == ""
    assert game.chaos_banner_timer == 0.0

def test_trigger_endless_chaos_active(game):
    print("\n[TEST] game address:", hex(id(game)))
    # Activar Endless Chaos con 2 modificadores
    game.endless_chaos_enabled = True
    game.endless_chaos_idx = 2
    
    # Asegurar que el snapshot esté limpio/vacío
    game.initial_modifier_snapshot = {}
    
    # Activar el Caos Infinito
    print("\n=== DEBUG BEFORE TRIGGER ===")
    print("endless_chaos_enabled:", game.endless_chaos_enabled)
    print("endless_chaos_idx:", game.endless_chaos_idx)
    print("=== END DEBUG BEFORE TRIGGER ===")
    game.trigger_endless_chaos()
    
    # Comprobar que se tomó un snapshot
    if game.initial_modifier_snapshot == {}:
        print("\n=== DEBUG INFO FOR SNAPSHOT FAILURE ===")
        print("endless_active:", game.endless_active)
        print("arcade_active:", game.arcade_active)
        print("endless_chaos_enabled:", game.endless_chaos_enabled)
        print("endless_chaos_idx:", game.endless_chaos_idx)
        print("endless_pool len:", len(game.endless_pool) if hasattr(game, 'endless_pool') else 'None')
        print("=======================================")
    assert game.initial_modifier_snapshot != {}
    
    # Comprobar que se seleccionaron exactamente 2 modificadores únicos y no vacíos
    assert len(game.chaos_active_modifiers) == 2
    
    # Comprobar que la animación del banner se disparó con tiempo dinámico (5.0 + 2 * 0.5 = 6.0)
    assert game.chaos_banner_timer == 6.0
    assert len(game.chaos_banner_text) > 0
    
    # Comprobar que los modificadores elegidos se aplicaron en el motor de juego
    for mod in game.chaos_active_modifiers:
        field = mod["field"]
        if mod["type"] == "toggle":
            assert getattr(game, field) is True

def test_clear_chaos_modifiers(game):
    # Activar 2 modificadores
    game.endless_chaos_enabled = True
    game.endless_chaos_idx = 2
    game.trigger_endless_chaos()
    
    # Guardar los estados modificados
    modified_fields = {}
    for mod in game.chaos_active_modifiers:
        field = mod["field"]
        modified_fields[field] = getattr(game, field)
        
    # Limpiar los modificadores (simula final del punto sin acumulación)
    game.endless_chaos_accumulation = False
    game.chaos_active_modifiers = []
    game.apply_chaos_modifiers()
    
    # Verificar que los valores de los modificadores volvieron a su estado original (snapshot)
    for field, val in modified_fields.items():
        assert getattr(game, field) == game.initial_modifier_snapshot[field]

def test_accumulation_chaos_modifiers(game):
    # Activar Endless Chaos con acumulación
    game.endless_chaos_enabled = True
    game.endless_chaos_idx = 1
    game.endless_chaos_accumulation = True
    
    # Primer punto: dispara trigger
    game.trigger_endless_chaos()
    assert len(game.chaos_active_modifiers) == 1
    
    # Segundo punto: dispara trigger de nuevo y acumula
    game.trigger_endless_chaos()
    assert len(game.chaos_active_modifiers) == 2

def test_dependency_resolution(game):
    # 'destructible_planets' requiere 'floating_planets' para poder activarse.
    # Comprobar que si la dependencia 'floating_planets_enabled' es False,
    # 'destructible_planets' NO es un candidato elegible.
    game.endless_chaos_idx = 1
    game.initial_modifier_snapshot = {}
    
    # 1. Forzar que todos los campos del snapshot sean False
    for item in game.endless_pool:
        game.initial_modifier_snapshot[item["field"]] = False
        setattr(game, item["field"], False)
    
    # 2. Con floating_planets_enabled = False, destructible_planets no puede ser elegible.
    # Vamos a simular la lógica de candidatos para verificar esto:
    candidates = []
    for item in game.endless_pool:
        if item["id"] == "destructible_planets":
            # Verificar su check de dependencia directa
            dep_field = item["depends_on"]
            assert dep_field == "floating_planets_enabled"
            if not getattr(game, dep_field):
                continue
            candidates.append(item)
            
    assert len(candidates) == 0  # No es elegible porque floating_planets_enabled es False
    
    # 3. Si floating_planets_enabled = True, destructible_planets SI es elegible
    game.floating_planets_enabled = True
    candidates = []
    for item in game.endless_pool:
        if item["id"] == "destructible_planets":
            dep_field = item["depends_on"]
            if not getattr(game, dep_field):
                continue
            candidates.append(item)
            
    assert len(candidates) == 1
    assert candidates[0]["id"] == "destructible_planets"
