import pygame
import os

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.sounds_dir = "sounds"
        self.load_all_sounds()
        pygame.mixer.set_num_channels(32) # Suficientes canales para multibola

    def load_all_sounds(self):
        # Mapeo de archivos y volúmenes
        sound_configs = {
            "hit": ("hit.wav", 1.0),
            "pop": ("pop.wav", 1.0),
            "item_get": ("item_get.wav", 0.5),
            "error": ("error.wav", 0.5),
            "fire": ("fire.wav", 0.5),
            "uuui": ("uuui.wav", 0.8),
            "bell": ("campana.wav", 0.6),
            "divine": ("divino.wav", 0.8),
            "life": ("vida.wav", 0.8),
            "match_point": ("match_point_bell.wav", 0.8),
            "golden_goal": ("golden_goal.wav", 0.9),
            "explosion": ("explosion.wav", 1.0),
            "hadouken": ("hadouken.wav", 0.8),
            "x2": ("x2.wav", 0.9),
            "ghost": ("fantasma.wav", 1.0),
            "nom": ("nom.wav", 1.0),
            "squeak": ("squeak.wav", 0.5)
        }

        for name, (filename, volume) in sound_configs.items():
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                self.sounds[name] = sound
            else:
                print(f"Advertencia: No se encontró el sonido {path}")

    def play(self, name, loops=0, fadeout=0):
        if name in self.sounds:
            if fadeout > 0:
                self.sounds[name].fadeout(fadeout)
            else:
                self.sounds[name].play(loops)

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def fadeout(self, name, time):
        if name in self.sounds:
            self.sounds[name].fadeout(time)
