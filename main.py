import pygame
from game_engine import Game

if __name__ == "__main__":
    # Optimización de audio: pre-init antes de cualquier otra cosa
    pygame.mixer.pre_init(44100, -16, 2, 512)
    game = Game()
    game.run()
