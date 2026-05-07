import pygame
import os

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.sounds_dir = "sounds"
        self.master_volume = 0.5  # Volumen maestro (0.0 a 1.0)
        self.sound_base_volumes = {} # Guardamos los volúmenes base originales
        self.load_all_sounds()
        pygame.mixer.set_num_channels(32)

    def load_all_sounds(self):
        sound_configs = {
            "hit": ("hit.wav", 0.7),
            "pop": ("pop.wav", 0.7),
            "item_get": ("item_get.wav", 0.4),
            "error": ("error.wav", 0.4),
            "fire": ("fire.wav", 0.4),
            "uuui": ("uuui.wav", 0.6),
            "bell": ("campana.wav", 0.5),
            "divine": ("divino.wav", 0.6),
            "life": ("vida.wav", 0.6),
            "match_point": ("match_point_bell.wav", 0.6),
            "golden_goal": ("golden_goal.wav", 0.7),
            "explosion": ("explosion.wav", 0.8),
            "hadouken": ("hadouken.wav", 0.6),
            "x2": ("x2.wav", 0.7),
            "ghost": ("fantasma.wav", 0.8),
            "nom": ("nom.wav", 0.8),
            "squeak": ("squeak.wav", 0.4),
            "pium": ("pium.wav", 0.6)
        }

        for name, (filename, vol) in sound_configs.items():
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                self.sound_base_volumes[name] = vol # Guardamos el volumen relativo
                sound.set_volume(vol * self.master_volume)
            else:
                print(f"Advertencia: No se encontró el sonido {path}")

    def play(self, name, loops=0, fadeout=0):
        if name in self.sounds:
            # Actualizar volumen antes de reproducir por si cambió el master_volume
            self.sounds[name].set_volume(self.sound_base_volumes[name] * self.master_volume)
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
