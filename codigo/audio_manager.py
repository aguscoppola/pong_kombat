import pygame
import os
import sys

class AudioManager:
    def __init__(self):
        self.sounds = {}
        # v0.7.0 Fix: Usar rutas relativas para Web (Pygbag VFS)
        if os.name == "nt" and not os.environ.get("PYGBAG"): # Si no estamos en Pygbag/Web
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.sounds_dir = os.path.join(base_dir, "sounds")
        else:
            self.sounds_dir = "sounds"
        self.master_volume = 0.5  # Volumen maestro (0.0 a 1.0)
        self.sound_base_volumes = {} # Guardamos los volúmenes base originales
        
        # v0.7.0: Desactivar carga de audio en Web para evitar errores de formato .wav
        self.is_web = sys.platform == "emscripten"
        
        # v0.7.0 Fix: Carga diferida (Lazy Loading) para evitar bloqueos en móvil
        self.sound_configs = {
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
            "pium": ("pium.wav", 0.6),
            "reveal": ("reveal.wav", 0.6),
            "victory_arcade": ("victory_arcade.wav", 0.8),
            "sleep_shoot": ("sleep_shoot.wav", 0.7),
            "sleep": ("sleep.wav", 0.7),
            "rainy": ("rainy.wav", 0.03),
            "thunder": ("thunder.wav", 0.8)
        }
        
        pygame.mixer.set_num_channels(32)

    def _load_single_sound(self, name):
        """Carga un sonido individual de forma segura (Lazy Loading)"""
        if self.is_web: return False # v0.7.0 Silencio en Web
        if name in self.sound_configs:
            filename, vol = self.sound_configs[name]
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    self.sounds[name] = sound
                    self.sound_base_volumes[name] = vol
                    sound.set_volume(vol * self.master_volume)
                    return True
                except Exception as e:
                    print(f"Error cargando {name} desde {path}: {e}")
            else:
                print(f"Advertencia: No se encontró el sonido {path}")
        return False

    def play(self, name, loops=0, fadeout=0, fade_ms=0):
        if self.is_web: return # v0.7.0 Silencio en Web
        # Si el sonido no está cargado, intentamos cargarlo ahora (Lazy Loading)
        if name not in self.sounds:
            if not self._load_single_sound(name):
                return # No se pudo cargar, ignoramos para no romper el juego

        if name in self.sounds:
            self.sounds[name].set_volume(self.sound_base_volumes[name] * self.master_volume)
            if fadeout > 0:
                self.sounds[name].fadeout(fadeout)
            else:
                self.sounds[name].play(loops, fade_ms=fade_ms)
        else:
            # Silenciamos el log en producción para no saturar la consola del navegador
            pass

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def fadeout(self, name, time):
        if name in self.sounds:
            self.sounds[name].fadeout(time)

    def play_music(self, filename, volume=0.5, fade_ms=1500):
        if self.is_web: return # v0.7.0 Silencio en Web
        # v0.7.0 Smart Loader para Música
        base_name = os.path.splitext(filename)[0]
        ogg_path = os.path.join(self.sounds_dir, f"{base_name}.ogg")
        wav_path = os.path.join(self.sounds_dir, f"{base_name}.wav")
        
        path = ogg_path if os.path.exists(ogg_path) else wav_path
        
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume * self.master_volume)
                pygame.mixer.music.play(-1, fade_ms=fade_ms) # Loop eterno con FadeIn
            except Exception as e:
                print(f"Error cargando música {path}: {e}")

    def stop_music(self, fadeout_ms=1500):
        pygame.mixer.music.fadeout(fadeout_ms)

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume * self.master_volume)
