# Robotron 2084 - Link Edition

A Zelda-themed remake of the classic Robotron 2084 arcade game, built with Python and Pygame.

## Features

- Play as Link from The Legend of Zelda
- Power-up arrow system with three levels:
  - Level 1: White arrows (normal power)
  - Level 2: Gold arrows (medium power, unlocked after 3 consecutive hits)
  - Level 3: Red arrows (maximum power, unlocked after 6 consecutive hits)
- Wave-based enemy system
- Human rescue mechanics
- Score system with kill streaks and wave bonuses
- Sound effects and visual feedback

## Requirements

- Python 3.x
- Pygame
- NumPy (for sound generation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/robotron2084.git
cd robotron2084
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install pygame numpy
```

## Running the Game

1. Generate game assets:
```bash
python create_placeholder_images.py
python create_sound_effects.py
```

2. Start the game:
```bash
python robotron.py
```

## Controls

- WASD: Move Link
- Arrow keys: Shoot arrows
- Space: Pause game

## Gameplay Tips

- Build up your power level by hitting enemies consecutively
- Rescue humans for bonus points
- Watch out for your power level timer - it resets if you don't shoot for 2 seconds
- Clear waves for big score bonuses
- You're invincible for a few seconds after losing a life

## License

This project is open source and available under the MIT License. 