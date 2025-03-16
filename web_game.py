import pygame
import random
import math
import os
import asyncio
from particles import ParticleSystem, ScreenShake

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.joystick.init()

# Constants
WINDOW_SIZE = (800, 600)
PLAYER_SIZE = 32
PLAYER_SPEED = 5
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Initialize game components
screen = pygame.display.set_mode(WINDOW_SIZE)
game_surface = pygame.Surface(WINDOW_SIZE)
pygame.display.set_caption("Robotron 2084")

# Initialize systems
particle_system = ParticleSystem()
screen_shake = ScreenShake()

# Load assets
def load_image(name):
    try:
        path = os.path.join('web', 'assets', 'images', name)
        return pygame.image.load(path)
    except:
        # Fallback: create a colored rectangle
        surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        if 'player' in name:
            surf.fill(BLUE)
        elif 'enemy' in name:
            surf.fill(RED)
        elif 'human' in name:
            surf.fill(GREEN)
        elif 'bullet' in name or 'arrow' in name:
            surf.fill(WHITE)
        return surf

def load_sound(name):
    try:
        path = os.path.join('web', 'assets', 'sounds', name)
        return pygame.mixer.Sound(path)
    except:
        # Return a dummy sound object
        return type('DummySound', (), {'play': lambda: None})()

# Load game assets
player_img = load_image('player.png')
enemy_img = load_image('enemy.png')
human_img = load_image('human.png')
bullet_img = load_image('bullet.png')

# Load sounds
shoot_sound = load_sound('shoot.wav')
explosion_sound = load_sound('explosion.wav')
death_sound = load_sound('death.wav')
rescue_sound = load_sound('rescue.wav')
wave_clear_sound = load_sound('wave_clear.wav')

# Game classes (Player, Enemy, Bullet, Human) remain the same as in robotron.py
# ... copy all the class definitions here ...

class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.consecutive_hits = 0
        self.power_level = 1
        self.last_shot_time = 0
        self.shoot_direction = [0, 0]
        self.last_trail_time = 0

    def update(self, keys, controller=None):
        current_time = pygame.time.get_ticks()
        
        # Create trail particles
        if current_time - self.last_trail_time > 50:
            particle_system.create_trail(self.pos[0] + PLAYER_SIZE/2, 
                                      self.pos[1] + PLAYER_SIZE/2, 
                                      WHITE)
            self.last_trail_time = current_time

        # Movement
        dx = dy = 0
        if controller:
            # Controller movement
            axis_x = controller.get_axis(0)
            axis_y = controller.get_axis(1)
            if abs(axis_x) > 0.1:
                dx = axis_x * self.speed
            if abs(axis_y) > 0.1:
                dy = axis_y * self.speed
            
            # Controller shooting
            shoot_x = controller.get_axis(2)
            shoot_y = controller.get_axis(3)
            if abs(shoot_x) > 0.1 or abs(shoot_y) > 0.1:
                self.shoot_direction = [shoot_x, shoot_y]
                return True
        else:
            # Keyboard movement
            if keys[pygame.K_a]: dx = -self.speed
            if keys[pygame.K_d]: dx = self.speed
            if keys[pygame.K_w]: dy = -self.speed
            if keys[pygame.K_s]: dy = self.speed
            
            # Keyboard shooting
            shooting = False
            self.shoot_direction = [0, 0]
            if keys[pygame.K_LEFT]:
                self.shoot_direction[0] = -1
                shooting = True
            if keys[pygame.K_RIGHT]:
                self.shoot_direction[0] = 1
                shooting = True
            if keys[pygame.K_UP]:
                self.shoot_direction[1] = -1
                shooting = True
            if keys[pygame.K_DOWN]:
                self.shoot_direction[1] = 1
                shooting = True
            
            if shooting:
                return True

        # Update position
        self.pos[0] = max(0, min(WINDOW_SIZE[0] - PLAYER_SIZE, self.pos[0] + dx))
        self.pos[1] = max(0, min(WINDOW_SIZE[1] - PLAYER_SIZE, self.pos[1] + dy))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        return False

    def draw(self, surface):
        surface.blit(player_img, self.pos)

class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = 2
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)

    def update(self, player_pos):
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def draw(self, surface):
        surface.blit(enemy_img, self.pos)

class Bullet:
    def __init__(self, x, y, dx, dy, power_level=1):
        self.pos = [x, y]
        speed = 10
        self.dx = dx * speed
        self.dy = dy * speed
        self.rect = pygame.Rect(x, y, 8, 8)
        self.power_level = power_level

    def update(self):
        self.pos[0] += self.dx
        self.pos[1] += self.dy
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        return (self.pos[0] < -10 or self.pos[0] > WINDOW_SIZE[0] + 10 or
                self.pos[1] < -10 or self.pos[1] > WINDOW_SIZE[1] + 10)

    def draw(self, surface):
        color = WHITE
        if self.power_level == 2:
            color = YELLOW
        elif self.power_level == 3:
            color = RED
        pygame.draw.circle(surface, color, (int(self.pos[0]), int(self.pos[1])), 4)

class Human:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.rescued = False

    def draw(self, surface):
        surface.blit(human_img, self.pos)

async def game_loop():
    # Initialize game state
    clock = pygame.time.Clock()
    running = True
    paused = False
    score = 0
    wave = 1
    player_lives = 3
    kill_streak = 0
    humans_rescued = 0
    invincible = False
    invincible_timer = 0
    INVINCIBLE_DURATION = 180
    INVINCIBLE_FLASH_RATE = 30
    
    # Initialize game objects
    player_pos = [WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2]
    player = Player(*player_pos)
    enemies = [Enemy(
        random.randint(0, WINDOW_SIZE[0]),
        random.randint(0, WINDOW_SIZE[1])
    ) for _ in range(5)]
    bullets = []
    humans = []
    
    # Font setup
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    
    # Controller setup
    controllers = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for controller in controllers:
        controller.init()

    # Game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7:  # Start button
                    paused = not paused

        if not paused:
            # Get controller
            controller = controllers[0] if controllers else None
            
            # Handle continuous keyboard input
            keys = pygame.key.get_pressed()
            
            # Update player
            if player.update(keys, controller):
                # Shooting
                if player.shoot_direction != [0, 0]:
                    dx, dy = player.shoot_direction
                    length = math.sqrt(dx*dx + dy*dy)
                    if length != 0:
                        dx /= length
                        dy /= length
                        bullets.append(Bullet(
                            player.pos[0] + PLAYER_SIZE//2,
                            player.pos[1] + PLAYER_SIZE//2,
                            dx, dy, player.power_level
                        ))
                        if shoot_sound:
                            shoot_sound.play()

            # Update invincibility
            if invincible:
                invincible_timer -= 1
                if invincible_timer <= 0:
                    invincible = False

            # Update bullets
            bullets = [b for b in bullets if not b.update()]
            
            # Update enemies
            for enemy in enemies:
                enemy.update(player.pos)
                
                # Check for collision with player
                if not invincible and enemy.rect.colliderect(player.rect):
                    player_lives -= 1
                    if death_sound:
                        death_sound.play()
                    if player_lives <= 0:
                        running = False
                    else:
                        invincible = True
                        invincible_timer = INVINCIBLE_DURATION
                        player.pos = [WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2]
                        player.rect.x = player.pos[0]
                        player.rect.y = player.pos[1]

            # Update particles and screen shake
            particle_system.update()
            screen_shake.update()

            # Check bullet collisions
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        if explosion_sound:
                            explosion_sound.play()
                        particle_system.create_explosion(enemy.rect.centerx, enemy.rect.centery, 
                                                      (255, 100, 0))
                        screen_shake.start_shake(3)
                        score += 100 * (kill_streak + 1)
                        kill_streak += 1
                        player.consecutive_hits += 1
                        if player.consecutive_hits >= 6:
                            player.power_level = 3
                            particle_system.create_power_up_effect(player.rect.centerx, player.rect.centery, RED)
                        elif player.consecutive_hits >= 3:
                            player.power_level = 2
                            particle_system.create_power_up_effect(player.rect.centerx, player.rect.centery, YELLOW)
                        break

            # Clear the game surface
            game_surface.fill(BLACK)
            
            # Draw game elements
            if not invincible or (invincible and pygame.time.get_ticks() // INVINCIBLE_FLASH_RATE % 2):
                player.draw(game_surface)
            
            for bullet in bullets:
                bullet.draw(game_surface)
            
            for enemy in enemies:
                enemy.draw(game_surface)

            for human in humans:
                human.draw(game_surface)

            # Draw particles
            particle_system.draw(game_surface)

            # Draw UI elements
            score_text = font.render(f"Score: {score}", True, WHITE)
            humans_text = font.render(f"Humans Rescued: {humans_rescued}", True, GREEN)
            wave_text = font.render(f"Wave: {wave}", True, YELLOW)
            lives_text = font.render(f"Lives: {player_lives}", True, RED)
            game_surface.blit(score_text, (10, 10))
            game_surface.blit(humans_text, (10, 50))
            game_surface.blit(wave_text, (10, 90))
            game_surface.blit(lives_text, (10, 130))

            if kill_streak > 1:
                streak_text = font.render(f"Streak: x{kill_streak}", True, ORANGE)
                game_surface.blit(streak_text, (10, 170))

            if invincible:
                inv_text = font.render(f"Invincible: {invincible_timer // 60 + 1}", True, YELLOW)
                game_surface.blit(inv_text, (WINDOW_SIZE[0] - 150, 10))

            # Apply screen shake and draw final frame
            shaken_surface, offset = screen_shake.apply(game_surface)
            screen.blit(shaken_surface, offset)

            # Check if wave is cleared
            if not enemies:
                wave += 1
                # Wave clear bonus
                wave_clear_bonus = wave * 1000
                score += wave_clear_bonus
                if wave_clear_sound:
                    wave_clear_sound.play()
                
                # Spawn more enemies
                enemies = [Enemy(
                    random.randint(-20, WINDOW_SIZE[0] + 20),
                    random.randint(-20, WINDOW_SIZE[1] + 20)
                ) for _ in range(5 + wave)]

        # Draw pause screen if paused
        if paused:
            pause_text = big_font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
            screen.blit(pause_text, text_rect)

        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
        
        # Required for web
        await asyncio.sleep(0)

    # Game Over screen
    screen.fill(BLACK)
    game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
    rescued_text = font.render(f"Humans Rescued: {humans_rescued}", True, GREEN)
    text_rect = game_over_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
    rescued_rect = rescued_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 40))
    screen.blit(game_over_text, text_rect)
    screen.blit(rescued_text, rescued_rect)
    pygame.display.flip()
    
    # Wait before quitting
    await asyncio.sleep(3)

# Start the game
asyncio.run(game_loop()) 