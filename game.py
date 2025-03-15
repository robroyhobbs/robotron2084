import pygame
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, power_level=1):
        super().__init__()
        self.power_level = power_level
        self.image = pygame.image.load(f'assets/images/arrow{power_level}.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        speed = 10 * (1 + (power_level - 1) * 0.5)  # Arrows get faster with power
        self.dx = dx * speed
        self.dy = dy * speed
        # Rotate the arrow image to face the direction it's moving
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/images/player.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.shoot_cooldown = 0
        self.consecutive_hits = 0
        self.power_level = 1
        self.last_shot_time = 0
        self.power_reset_timer = 0

    def update(self, joystick):
        # Movement
        x_move = joystick.get_axis(0)
        y_move = joystick.get_axis(1)
        
        if abs(x_move) > 0.1:
            self.rect.x += x_move * self.speed
        if abs(y_move) > 0.1:
            self.rect.y += y_move * self.speed
            
        # Keep player on screen
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        
        # Update power reset timer
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > 2000:  # Reset power after 2 seconds of not shooting
            self.consecutive_hits = 0
            self.power_level = 1

    def shoot(self, joystick):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < 250:  # Minimum time between shots
            return None
            
        x_aim = joystick.get_axis(3)
        y_aim = joystick.get_axis(4)
        
        if abs(x_aim) > 0.1 or abs(y_aim) > 0.1:
            # Normalize the direction vector
            length = math.sqrt(x_aim * x_aim + y_aim * y_aim)
            dx = x_aim / length
            dy = y_aim / length
            
            # Create a new bullet
            bullet = Bullet(self.rect.centerx, self.rect.centery, dx, dy, self.power_level)
            self.last_shot_time = current_time
            return bullet
        return None

    def power_up(self):
        self.consecutive_hits += 1
        if self.consecutive_hits >= 6:
            self.power_level = 3
        elif self.consecutive_hits >= 3:
            self.power_level = 2
        self.last_shot_time = pygame.time.get_ticks()  # Reset the power timer

def handle_bullet_collisions(bullets, enemies, player):
    # Check for collisions between bullets and enemies
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, True)
        if hits:
            player.power_up()  # Power up on successful hit
            bullet.kill()
            return len(hits)
    return 0 