import sys
import os

# Rutas absolutas para evitar errores de importación
BASE_DIR = r"c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat"
sys.path.append(os.path.join(BASE_DIR, "codigo_fuente"))
sys.path.append(os.path.join(BASE_DIR, "codigo"))

if __name__ == "__main__":
    from game_engine import Game
    game = Game()
    game.run()
