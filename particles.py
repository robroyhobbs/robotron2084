import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity=None, lifetime=60, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        if velocity:
            self.dx = velocity[0]
            self.dy = velocity[1]
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.dx = math.cos(angle) * speed
            self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, surface):
        alpha = int((self.lifetime / self.max_lifetime) * 255)
        color = (*self.color[:3], alpha) if len(self.color) > 3 else (*self.color, alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size, self.size), self.size)
        surface.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def create_explosion(self, x, y, color, num_particles=20):
        for _ in range(num_particles):
            self.particles.append(Particle(x, y, color))

    def create_trail(self, x, y, color):
        self.particles.append(Particle(x, y, color, velocity=(0, 0), lifetime=20, size=2))

    def create_power_up_effect(self, x, y, color):
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            dx = math.cos(angle) * 2
            dy = math.sin(angle) * 2
            self.particles.append(Particle(x, y, color, velocity=(dx, dy), lifetime=30))

    def update(self):
        self.particles = [p for p in self.particles if not p.update()]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0

    def start_shake(self, intensity, duration=10):
        self.duration = duration
        self.intensity = intensity

    def update(self):
        if self.duration > 0:
            self.duration -= 1

    def apply(self, surface):
        if self.duration <= 0:
            return surface, (0, 0)

        offset_x = random.randint(-self.intensity, self.intensity)
        offset_y = random.randint(-self.intensity, self.intensity)
        return surface, (offset_x, offset_y) 