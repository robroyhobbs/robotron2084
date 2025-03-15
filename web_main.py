import asyncio
import pygame
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Import game modules
import robotron
from particles import ParticleSystem, ScreenShake

async def main():
    # Initialize game
    particle_system = ParticleSystem()
    screen_shake = ScreenShake()
    
    # Start the game loop
    await robotron.game_loop()

# Start the game
asyncio.run(main()) 