import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity=None, lifetime=30, size=3, decay=0.9, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.original_color = color
        self.alpha = 255
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.original_size = size
        self.decay = decay
        self.glow = glow
        
        if velocity:
            self.dx, self.dy = velocity
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            self.dx = math.cos(angle) * speed
            self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.size *= self.decay
        
        # Calculate alpha based on remaining lifetime
        life_ratio = self.lifetime / self.max_lifetime
        self.alpha = max(0, min(255, int(255 * life_ratio)))
        
        # Adjust color based on lifetime
        if self.glow:
            glow_intensity = min(255, int(255 * (1 - life_ratio)))
            r = min(255, self.original_color[0] + glow_intensity)
            g = min(255, self.original_color[1] + glow_intensity)
            b = min(255, self.original_color[2] + glow_intensity)
            self.color = (r, g, b)

    def draw(self, surface):
        if self.lifetime <= 0:
            return False
            
        if self.glow:
            # Create a glowing effect using multiple circles
            glow_surf = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
            center = (int(self.size * 2), int(self.size * 2))
            
            for radius in [self.size * 2, self.size * 1.5, self.size]:
                glow_color = (*self.color, self.alpha // (4 if radius > self.size else 1))
                pygame.draw.circle(glow_surf, glow_color, center, radius)
            
            surface.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))
        else:
            # Regular particle
            particle_surf = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            particle_color = (*self.color, self.alpha)
            pygame.draw.circle(particle_surf, particle_color, 
                             (int(self.size/2), int(self.size/2)), 
                             max(1, int(self.size/2)))
            surface.blit(particle_surf, (self.x, self.y))
        
        return True

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def create_explosion(self, x, y, color, particle_count=20):
        for _ in range(particle_count):
            particle = Particle(x, y, color, lifetime=random.randint(20, 40),
                              size=random.uniform(2, 4), glow=True)
            self.particles.append(particle)

    def create_power_up_effect(self, x, y, color):
        # Create a spiral effect
        for i in range(20):
            angle = (i / 20) * 2 * math.pi
            speed = random.uniform(2, 4)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            particle = Particle(x, y, color, velocity=(dx, dy),
                              lifetime=40, size=3, glow=True)
            self.particles.append(particle)

    def create_trail(self, x, y, color):
        # Create a subtle trailing effect
        particle = Particle(x, y, color, lifetime=10, size=2,
                          velocity=(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))
        self.particles.append(particle)

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class ScreenShake:
    def __init__(self):
        self.shake_offset = [0, 0]
        self.shake_intensity = 0
        self.shake_decay = 0.9

    def start_shake(self, intensity=5):
        self.shake_intensity = intensity

    def update(self):
        if self.shake_intensity > 0.1:
            self.shake_offset[0] = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset[1] = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= self.shake_decay
        else:
            self.shake_offset = [0, 0]
            self.shake_intensity = 0

    def apply(self, surface):
        return surface.copy(), self.shake_offset 