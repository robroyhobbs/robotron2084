import pygame
import random
import math

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

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)

class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.consecutive_hits = 0
        self.power_level = 1
        self.shoot_direction = [0, 0]
        self.last_shot_time = 0

    def update(self, keys):
        # Movement
        dx = dy = 0
        if keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_s]: dy = self.speed
        
        # Shooting
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

        # Update position
        self.pos[0] = max(0, min(WINDOW_SIZE[0] - PLAYER_SIZE, self.pos[0] + dx))
        self.pos[1] = max(0, min(WINDOW_SIZE[1] - PLAYER_SIZE, self.pos[1] + dy))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        return shooting

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

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
        pygame.draw.rect(surface, RED, self.rect)

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

def game_loop():
    clock = pygame.time.Clock()

    # Game state
    running = True
    paused = False
    score = 0
    wave = 1
    player_lives = 3
    kill_streak = 0
    invincible = False
    invincible_timer = 0
    INVINCIBLE_DURATION = 180
    INVINCIBLE_FLASH_RATE = 30

    # Game objects
    player = Player(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2)
    enemies = [Enemy(
        random.randint(0, WINDOW_SIZE[0]),
        random.randint(0, WINDOW_SIZE[1])
    ) for _ in range(5)]
    bullets = []

    # Font setup
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)

    def game_frame():
        nonlocal running, paused, score, wave, player_lives, kill_streak
        nonlocal invincible, invincible_timer, enemies, bullets

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            # Handle continuous keyboard input
            keys = pygame.key.get_pressed()
            
            # Update player
            if player.update(keys):
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
                    if player_lives <= 0:
                        running = False
                    else:
                        invincible = True
                        invincible_timer = INVINCIBLE_DURATION
                        player.pos = [WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2]
                        player.rect.x = player.pos[0]
                        player.rect.y = player.pos[1]

            # Check bullet collisions
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        score += 100 * (kill_streak + 1)
                        kill_streak += 1
                        player.consecutive_hits += 1
                        if player.consecutive_hits >= 6:
                            player.power_level = 3
                        elif player.consecutive_hits >= 3:
                            player.power_level = 2
                        break

            # Clear the screen
            screen.fill(BLACK)
            
            # Draw game elements
            if not invincible or (invincible and pygame.time.get_ticks() // INVINCIBLE_FLASH_RATE % 2):
                player.draw(screen)
            
            for bullet in bullets:
                bullet.draw(screen)
            
            for enemy in enemies:
                enemy.draw(screen)

            # Draw UI elements
            score_text = font.render(f"Score: {score}", True, WHITE)
            wave_text = font.render(f"Wave: {wave}", True, YELLOW)
            lives_text = font.render(f"Lives: {player_lives}", True, RED)
            screen.blit(score_text, (10, 10))
            screen.blit(wave_text, (10, 50))
            screen.blit(lives_text, (10, 90))

            if kill_streak > 1:
                streak_text = font.render(f"Streak: x{kill_streak}", True, ORANGE)
                screen.blit(streak_text, (10, 130))

            if invincible:
                inv_text = font.render(f"Invincible: {invincible_timer // 60 + 1}", True, YELLOW)
                screen.blit(inv_text, (WINDOW_SIZE[0] - 150, 10))

            # Check if wave is cleared
            if not enemies:
                wave += 1
                # Wave clear bonus
                wave_clear_bonus = wave * 1000
                score += wave_clear_bonus
                
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

        if running:
            pygame.window.requestAnimationFrame(game_frame)
        else:
            # Game Over screen
            screen.fill(BLACK)
            game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
            screen.blit(game_over_text, text_rect)
            pygame.display.flip()

    # Start the game loop
    pygame.window.requestAnimationFrame(game_frame)

# Start the game
game_loop() 