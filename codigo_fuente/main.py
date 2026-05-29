import sys
import os

# Determinamos la ruta base dependiendo de si corremos como .py o como .exe
if getattr(sys, 'frozen', False):
    # Estamos en un .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Estamos en modo desarrollo (script .py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Añadimos las carpetas al path de forma dinámica
sys.path.append(os.path.join(BASE_DIR, "codigo_fuente"))
sys.path.append(os.path.join(BASE_DIR, "codigo"))

# Esto imprimirá la ruta en la consola antes de que el juego arranque
print(f"Buscando save_data en: {os.path.join(BASE_DIR, 'save_data.json')}")

if __name__ == "__main__":
    from codigo_fuente.game_engine import Game
    game = Game()
    game.run()
