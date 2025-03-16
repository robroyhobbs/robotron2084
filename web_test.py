import pygame
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Black background
        pygame.draw.rect(screen, (255, 0, 0), (350, 250, 100, 100))  # Red square
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main()) 