import pygame

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((400, 300))

def game_loop():
    # Game state
    running = True

    def game_frame():
        nonlocal running

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw a test rectangle
        pygame.draw.rect(screen, (255, 0, 0), (175, 125, 50, 50))
        
        # Update display
        pygame.display.flip()

        if running:
            pygame.window.requestAnimationFrame(game_frame)

    # Start the game loop
    pygame.window.requestAnimationFrame(game_frame)

# Start the game
game_loop() 