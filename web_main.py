import asyncio
import pygame
import sys
import os
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up paths for web
ASSETS_DIR = Path('web/assets')
IMAGES_DIR = ASSETS_DIR / 'images'
SOUNDS_DIR = ASSETS_DIR / 'sounds'

# Make sure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Import game modules
import robotron
from particles import ParticleSystem, ScreenShake

async def main():
    try:
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up display
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Robotron 2084 - Link Edition")
        
        # Game loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Draw a test rectangle
            pygame.draw.rect(screen, (255, 255, 255), (100, 100, 50, 50))
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            clock.tick(60)
            
            # Required for web
            await asyncio.sleep(0)
            
    except Exception as e:
        print(f"Error in web_main: {str(e)}")
        raise

# Start the game
asyncio.run(main()) 