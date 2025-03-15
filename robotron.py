import pygame
import random
import math
import os

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()
pygame.joystick.init()  # Initialize joystick support

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

# Set up the display first
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Robotron 2084")

# Set up controller
controllers = []
for i in range(pygame.joystick.get_count()):
    controller = pygame.joystick.Joystick(i)
    controller.init()
    controllers.append(controller)
    print(f"Found controller: {controller.get_name()}")

# Controller settings
DEADZONE = 0.2  # Ignore small stick movements
TRIGGER_THRESHOLD = 0.1  # Minimum trigger pull to register

# Asset loading
def load_image(name):
    try:
        path = os.path.join('assets', 'images', name)
        print(f"Loading image from: {os.path.abspath(path)}")
        if not os.path.exists(path):
            print(f"File does not exist: {path}")
            raise FileNotFoundError
        image = pygame.image.load(path)
        return image.convert_alpha()
    except Exception as e:
        print(f"Error loading image {name}: {str(e)}")
        # Create a surface with the default color if image loading fails
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, RED if "player" in name else BLUE if "enemy" in name else GREEN, surf.get_rect())
        return surf

def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join('assets', 'sounds', name))
    except:
        print(f"Couldn't load sound: {name}")
        return None

# Load images
player_img = load_image('player.png')
enemy_img = load_image('enemy.png')
human_img = load_image('human.png')
arrow_imgs = [load_image(f'arrow{i}.png') for i in range(1, 4)]

# Load sounds
shoot_sound = load_sound('shoot.wav')
explosion_sound = load_sound('explosion.wav')
rescue_sound = load_sound('rescue.wav')
death_sound = load_sound('death.wav')
wave_clear_sound = load_sound('wave_clear.wav')

class Bullet:
    def __init__(self, x, y, dx, dy, power_level=1):
        self.pos = [x, y]
        self.power_level = power_level
        self.speed = 10 * (1 + (power_level - 1) * 0.5)  # Arrows get faster with power
        self.dir = [dx, dy]
        self.rect = pygame.Rect(x, y, 16, 8)  # Adjusted size for arrows
        self.image = arrow_imgs[power_level - 1]
        # Rotate the arrow image to face the direction it's moving
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)
        if shoot_sound:
            shoot_sound.play()

    def update(self):
        self.pos[0] += self.dir[0] * self.speed
        self.pos[1] += self.dir[1] * self.speed
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def draw(self, surface):
        surface.blit(self.image, self.pos)

class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.consecutive_hits = 0
        self.power_level = 1
        self.last_shot_time = 0
        self.shoot_direction = [0, 0]  # For controller aiming

    def update(self, keys, controller=None):
        # Update power reset timer
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > 2000:
            self.consecutive_hits = 0
            self.power_level = 1

        # Movement
        move_x = 0
        move_y = 0

        if controller:
            # Left stick movement
            left_x = controller.get_axis(0)
            left_y = controller.get_axis(1)
            if abs(left_x) > DEADZONE:
                move_x = left_x
            if abs(left_y) > DEADZONE:
                move_y = left_y

            # Right stick aiming
            right_x = controller.get_axis(3)
            right_y = controller.get_axis(4)
            if abs(right_x) > DEADZONE or abs(right_y) > DEADZONE:
                self.shoot_direction = [right_x, right_y]
            
        else:
            # Keyboard movement
            if keys[pygame.K_a]: move_x = -1
            if keys[pygame.K_d]: move_x = 1
            if keys[pygame.K_w]: move_y = -1
            if keys[pygame.K_s]: move_y = 1

            # Keyboard aiming
            if keys[pygame.K_LEFT]: self.shoot_direction = [-1, 0]
            elif keys[pygame.K_RIGHT]: self.shoot_direction = [1, 0]
            elif keys[pygame.K_UP]: self.shoot_direction = [0, -1]
            elif keys[pygame.K_DOWN]: self.shoot_direction = [0, 1]

        # Apply movement
        self.pos[0] += move_x * self.speed
        self.pos[1] += move_y * self.speed

        # Keep player on screen
        self.pos[0] = max(0, min(self.pos[0], WINDOW_SIZE[0] - PLAYER_SIZE))
        self.pos[1] = max(0, min(self.pos[1], WINDOW_SIZE[1] - PLAYER_SIZE))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        # Update global player position (for compatibility)
        global player_pos
        player_pos[0] = self.pos[0]
        player_pos[1] = self.pos[1]
        player_rect.x = self.pos[0]
        player_rect.y = self.pos[1]

    def power_up(self):
        self.consecutive_hits += 1
        if self.consecutive_hits >= 6:
            self.power_level = 3
        elif self.consecutive_hits >= 3:
            self.power_level = 2
        self.last_shot_time = pygame.time.get_ticks()

    def try_shoot(self, controller=None):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < 250:  # Minimum time between shots
            return None

        if controller:
            # Right stick shooting
            right_x = controller.get_axis(3)
            right_y = controller.get_axis(4)
            if abs(right_x) > DEADZONE or abs(right_y) > DEADZONE:
                # Normalize the direction vector
                length = math.sqrt(right_x * right_x + right_y * right_y)
                dx = right_x / length
                dy = right_y / length
                bullet = Bullet(self.rect.centerx, self.rect.centery, dx, dy, self.power_level)
                self.last_shot_time = current_time
                return bullet
        else:
            # Keyboard shooting
            if any(self.shoot_direction):
                dx, dy = self.shoot_direction
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
                bullet = Bullet(self.rect.centerx, self.rect.centery, dx, dy, self.power_level)
                self.last_shot_time = current_time
                return bullet
        return None

class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = 2
        self.rect = pygame.Rect(x, y, 32, 32)  # Adjusted size for sprite

    def update(self, target):
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.pos[0] += self.speed * dx / dist
        self.pos[1] += self.speed * dy / dist
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def draw(self, surface):
        surface.blit(enemy_img, self.pos)

class Human:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.rect = pygame.Rect(x, y, 32, 32)  # Adjusted size for sprite

    def draw(self, surface):
        surface.blit(human_img, self.pos)

# Player setup
player = Player(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
player_pos = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)
player_lives = 3
invincible = True
invincible_timer = 300  # 5 seconds at 60 FPS
INVINCIBLE_DURATION = 300
INVINCIBLE_FLASH_RATE = 15  # How often to flash when invincible

# Bullet setup
bullets = []
shoot_cooldown = 0
SHOOT_DELAY = 10

# Enemy setup
wave = 1
enemies = [Enemy(random.randint(0, WINDOW_SIZE[0]), random.randint(0, WINDOW_SIZE[1])) for _ in range(5)]
ENEMY_SPAWN_DELAY = 180
enemy_spawn_timer = ENEMY_SPAWN_DELAY

# Human setup
RESCUE_DISTANCE = 20
humans = [Human(random.randint(0, WINDOW_SIZE[0]), random.randint(0, WINDOW_SIZE[1])) for _ in range(3)]
humans_rescued = 0
HUMAN_SPAWN_DELAY = 300  # Spawn new human every 5 seconds
human_spawn_timer = HUMAN_SPAWN_DELAY

# Score setup
score = 0
kill_streak = 0
kill_streak_timer = 0
STREAK_TIMEOUT = 120  # 2 seconds at 60 FPS
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 74)  # Larger font for pause screen

# Game state
paused = False

# Game loop
clock = pygame.time.Clock()
running = True

def reset_player():
    global player_pos, invincible, invincible_timer, player
    player_pos = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
    player_rect.x = player_pos[0]
    player_rect.y = player_pos[1]
    player = Player(player_pos[0], player_pos[1])
    invincible = True
    invincible_timer = INVINCIBLE_DURATION

# Update bullet collision handling
def handle_bullet_collision(bullet, enemy):
    if bullet.rect.colliderect(enemy.rect):
        enemies.remove(enemy)
        bullets.remove(bullet)
        if explosion_sound:
            explosion_sound.play()
        return True
    return False

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:  # Start button on Xbox controller
                paused = not paused

    if not paused:
        # Get controller if available
        controller = controllers[0] if controllers else None
        
        # Handle continuous keyboard input
        keys = pygame.key.get_pressed()
        
        # Update player
        player.update(keys, controller)
        
        # Handle shooting
        if shoot_cooldown > 0:
            shoot_cooldown -= 1
        else:
            bullet = player.try_shoot(controller)
            if bullet:
                bullets.append(bullet)
                shoot_cooldown = SHOOT_DELAY

        # Update invincibility
        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False

        # Update and check bullets
        for bullet in bullets[:]:
            bullet.update()
            if not (0 <= bullet.pos[0] <= WINDOW_SIZE[0] and 0 <= bullet.pos[1] <= WINDOW_SIZE[1]):
                bullets.remove(bullet)
                continue
            
            for enemy in enemies[:]:
                if handle_bullet_collision(bullet, enemy):
                    player.power_up()
                    
                    # Update kill streak and score
                    kill_streak += 1
                    kill_streak_timer = STREAK_TIMEOUT
                    
                    # Base score + streak bonus + wave bonus + power level bonus
                    kill_score = 100 * (1 + kill_streak * 0.1)  # 10% more for each kill in streak
                    power_bonus = (player.power_level - 1) * 50  # 50 points extra per power level
                    wave_bonus = wave * 10  # 10 points extra per wave
                    score += int(kill_score + wave_bonus + power_bonus)
                    break

        # Update kill streak timer
        if kill_streak_timer > 0:
            kill_streak_timer -= 1
        elif kill_streak > 0:
            kill_streak = 0

        # Update enemies
        for enemy in enemies[:]:
            enemy.update([player_pos[0] + PLAYER_SIZE/2, player_pos[1] + PLAYER_SIZE/2])
            if enemy.rect.colliderect(player_rect) and not invincible:
                if death_sound:
                    death_sound.play()
                player_lives -= 1
                if player_lives > 0:
                    reset_player()
                    # Clear nearby enemies to prevent instant death
                    for e in enemies[:]:
                        if (abs(e.pos[0] - player_pos[0]) < PLAYER_SIZE * 4 and 
                            abs(e.pos[1] - player_pos[1]) < PLAYER_SIZE * 4):
                            enemies.remove(e)
                else:
                    running = False

            # Check if enemy catches a human
            for human in humans[:]:
                if enemy.rect.colliderect(human.rect):
                    humans.remove(human)
                    score -= 200

        # Check for human rescue
        for human in humans[:]:
            if abs(player_pos[0] + PLAYER_SIZE/2 - human.pos[0]) < RESCUE_DISTANCE and \
               abs(player_pos[1] + PLAYER_SIZE/2 - human.pos[1]) < RESCUE_DISTANCE:
                humans.remove(human)
                humans_rescued += 1
                score += 500
                if rescue_sound:
                    rescue_sound.play()

        # Spawn new enemies
        enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0:
            side = random.randint(0, 3)
            if side == 0:  # Top
                x = random.randint(0, WINDOW_SIZE[0])
                y = -20
            elif side == 1:  # Right
                x = WINDOW_SIZE[0] + 20
                y = random.randint(0, WINDOW_SIZE[1])
            elif side == 2:  # Bottom
                x = random.randint(0, WINDOW_SIZE[0])
                y = WINDOW_SIZE[1] + 20
            else:  # Left
                x = -20
                y = random.randint(0, WINDOW_SIZE[1])
            
            enemies.append(Enemy(x, y))
            enemy_spawn_timer = ENEMY_SPAWN_DELAY

        # Spawn new humans
        human_spawn_timer -= 1
        if human_spawn_timer <= 0 and len(humans) < 5:
            humans.append(Human(
                random.randint(50, WINDOW_SIZE[0] - 50),
                random.randint(50, WINDOW_SIZE[1] - 50)
            ))
            human_spawn_timer = HUMAN_SPAWN_DELAY

    # Drawing
    screen.fill(BLACK)
    
    # Draw game elements
    if not invincible or (invincible and pygame.time.get_ticks() // INVINCIBLE_FLASH_RATE % 2):
        screen.blit(player_img, player_pos)
    
    for bullet in bullets:
        bullet.draw(screen)
    
    for enemy in enemies:
        enemy.draw(screen)

    for human in humans:
        human.draw(screen)

    # Draw score, humans rescued, wave, and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    humans_text = font.render(f"Humans Rescued: {humans_rescued}", True, GREEN)
    wave_text = font.render(f"Wave: {wave}", True, YELLOW)
    lives_text = font.render(f"Lives: {player_lives}", True, RED)
    screen.blit(score_text, (10, 10))
    screen.blit(humans_text, (10, 50))
    screen.blit(wave_text, (10, 90))
    screen.blit(lives_text, (10, 130))

    # Draw kill streak if active
    if kill_streak > 1:
        streak_text = font.render(f"Streak: x{kill_streak}", True, ORANGE)
        screen.blit(streak_text, (10, 170))

    # Draw invincibility timer if active
    if invincible:
        inv_text = font.render(f"Invincible: {invincible_timer // 60 + 1}", True, YELLOW)
        screen.blit(inv_text, (WINDOW_SIZE[0] - 150, 10))

    # Check if all enemies are cleared to start new wave
    if not enemies and not paused:
        wave += 1
        # Wave clear bonus
        wave_clear_bonus = wave * 1000
        score += wave_clear_bonus
        
        # Spawn more enemies each wave
        enemies = [Enemy(
            random.randint(-20, WINDOW_SIZE[0] + 20),
            random.randint(-20, WINDOW_SIZE[1] + 20)
        ) for _ in range(5 + wave)]
        
        # Display wave start message and bonus
        wave_start_text = big_font.render(f"Wave {wave}", True, YELLOW)
        bonus_text = font.render(f"Wave Clear Bonus: +{wave_clear_bonus}", True, ORANGE)
        wave_start_rect = wave_start_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 - 20))
        bonus_rect = bonus_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 20))
        screen.blit(wave_start_text, wave_start_rect)
        screen.blit(bonus_text, bonus_rect)
        pygame.display.flip()
        pygame.time.wait(1500)  # Show bonus message a bit longer

    # Draw pause screen if paused
    if paused:
        # Create semi-transparent overlay
        overlay = pygame.Surface(WINDOW_SIZE)
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = big_font.render("PAUSED", True, YELLOW)
        continue_text = font.render("Press SPACE to continue", True, WHITE)
        
        pause_rect = pause_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 - 20))
        continue_rect = continue_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 20))
        
        screen.blit(pause_text, pause_rect)
        screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    clock.tick(60)

# Game Over screen
screen.fill(BLACK)
game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
rescued_text = font.render(f"Humans Rescued: {humans_rescued}", True, GREEN)
text_rect = game_over_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
rescued_rect = rescued_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 40))
screen.blit(game_over_text, text_rect)
screen.blit(rescued_text, rescued_rect)
pygame.display.flip()

# Wait a few seconds before quitting
pygame.time.wait(3000)

# Quit Pygame
pygame.quit()