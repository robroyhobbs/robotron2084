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
        # Initialize game components
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Robotron 2084 - Link Edition")
        
        # Initialize systems
        particle_system = ParticleSystem()
        screen_shake = ScreenShake()
        
        # Start the game loop
        await robotron.game_loop()
        
    except Exception as e:
        print(f"Error in web_main: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main()) 