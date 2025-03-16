import pygame
import asyncio

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

async def main():
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw a test rectangle
        pygame.draw.rect(screen, (255, 0, 0), (175, 125, 50, 50))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
        
        # Let other async tasks run
        await asyncio.sleep(0)

asyncio.run(main()) 