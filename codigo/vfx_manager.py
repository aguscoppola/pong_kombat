import pygame
import random
from entities import Particle
from constants import *

class VFXManager:
    def __init__(self):
        self.particles = []
        self.enabled = True

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def burst(self, x, y, color, count=15, lifetime=1.0):
        if not self.enabled: return
        for _ in range(count):
            self.particles.append(Particle(x, y, color, lifetime=lifetime))

    def explosion(self, x, y, color, count=60):
        if not self.enabled: return
        for _ in range(count):
            # Explosión más dispersa y duradera
            p = Particle(x, y, color, lifetime=random.uniform(0.5, 1.5))
            p.vx *= 1.5
            p.vy *= 1.5
            self.particles.append(p)

    def trail(self, x, y, color, count=1, lifetime=0.4):
        if not self.enabled: return
        for _ in range(count):
            self.particles.append(Particle(x, y, color, lifetime=lifetime))

    def confetti_rain(self, count=500):
        if not self.enabled: return
        colors = [RED, GREEN, BLUE, YELLOW, PINK, ORANGE, PURPLE, WHITE]
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            # Spawnear algunos dentro de la pantalla para efecto inmediato (v0.6.0 Fix)
            y = random.randint(-300, 300)
            self.particles.append(Particle(x, y, random.choice(colors), lifetime=6.0, is_confetti=True))

    def clear(self):
        self.particles.clear()
