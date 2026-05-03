import pygame
import random
from entities import Particle
from constants import *

class VFXManager:
    def __init__(self):
        self.particles = []

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def burst(self, x, y, color, count=15, lifetime=1.0):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, lifetime=lifetime))

    def explosion(self, x, y, color, count=60):
        for _ in range(count):
            # Explosión más dispersa y duradera
            p = Particle(x, y, color, lifetime=random.uniform(0.5, 1.5))
            p.vx *= 1.5
            p.vy *= 1.5
            self.particles.append(p)

    def trail(self, x, y, color, count=1, lifetime=0.4):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, lifetime=lifetime))

    def clear(self):
        self.particles.clear()
