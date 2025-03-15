import pygame
import os

# Initialize Pygame
pygame.init()

# Create assets directories if they don't exist
os.makedirs('assets/images', exist_ok=True)

# Colors for Link sprite
GREEN = (34, 177, 76)     # Tunic color
SKIN = (255, 219, 172)    # Skin tone
YELLOW = (255, 255, 0)    # Hair color
BROWN = (139, 69, 19)     # Belt/shoes color
SILVER = (192, 192, 192)  # Sword color
BLUE = (65, 105, 225)     # Shield color
RED = (255, 0, 0)        # Shield emblem color

def create_link_sprite():
    # Create a 32x32 surface with transparency
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # Draw tunic (body)
    pygame.draw.rect(surface, GREEN, (8, 12, 16, 16))
    
    # Draw head
    pygame.draw.rect(surface, SKIN, (10, 4, 12, 12))
    
    # Draw hair
    pygame.draw.rect(surface, YELLOW, (8, 4, 16, 6))
    
    # Draw belt
    pygame.draw.rect(surface, BROWN, (8, 24, 16, 4))
    
    # Draw legs
    pygame.draw.rect(surface, BROWN, (10, 28, 4, 4))  # Left leg
    pygame.draw.rect(surface, BROWN, (18, 28, 4, 4))  # Right leg
    
    # Draw shield (on left arm)
    pygame.draw.rect(surface, BLUE, (4, 14, 6, 10))    # Shield base
    pygame.draw.rect(surface, RED, (5, 16, 4, 4))      # Shield emblem
    
    # Draw sword (on right side)
    pygame.draw.rect(surface, BROWN, (24, 16, 4, 4))   # Sword handle
    pygame.draw.rect(surface, SILVER, (26, 8, 2, 8))   # Sword blade
    
    return surface

def create_arrow(power_level=1):
    # Create arrow with different colors based on power level
    size = (16, 8)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Arrow colors based on power level
    if power_level == 1:
        color = (255, 255, 255)  # White for normal arrows
    elif power_level == 2:
        color = (255, 215, 0)    # Gold for medium power
    else:
        color = (255, 0, 0)      # Red for max power
    
    # Draw arrow shaft
    pygame.draw.rect(surface, color, (4, 3, 8, 2))
    
    # Draw arrow head
    pygame.draw.polygon(surface, color, [(12, 0), (16, 4), (12, 8)])
    
    return surface

# Create Link sprite
link_sprite = create_link_sprite()
pygame.image.save(link_sprite, os.path.join('assets/images', 'player.png'))

# Create arrow images for different power levels
arrow1 = create_arrow(1)
arrow2 = create_arrow(2)
arrow3 = create_arrow(3)
pygame.image.save(arrow1, os.path.join('assets/images', 'arrow1.png'))
pygame.image.save(arrow2, os.path.join('assets/images', 'arrow2.png'))
pygame.image.save(arrow3, os.path.join('assets/images', 'arrow3.png'))

# Create other game images
def create_image(name, color, size=(32, 32)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, surface.get_rect())
    pygame.image.save(surface, os.path.join('assets/images', name))

# Create other game images
create_image('enemy.png', (0, 0, 255))
create_image('human.png', (0, 255, 0))

print("Images created successfully in assets/images/") 