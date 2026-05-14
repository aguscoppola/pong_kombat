import sys
import os
import asyncio
import pygame

# Configurar el path para encontrar el código en las carpetas de refactorización
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "codigo_fuente"))
sys.path.append(os.path.join(BASE_DIR, "codigo"))

async def main():
    from game_engine import Game
    game = Game()
    
    # Detectar si estamos en un navegador (pygbag)
    if sys.platform == "emscripten":
        await game.run_async()
    else:
        game.run()

if __name__ == "__main__":
    asyncio.run(main())
