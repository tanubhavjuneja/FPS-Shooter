# 3D FPS Game - Powered by Ursina Engine

## Overview

This is a 3D First-Person Shooter (FPS) game developed using the **Ursina Engine**, a Python-based game engine. The game allows the player to control a character (Iron Man), shoot energy beams, and battle enemies in a futuristic city environment. The game features dynamic enemy spawning, a health bar, shooting mechanics, and various UI elements.

## Features

- **First-Person Shooter (FPS) Gameplay:**
  - Control Iron Man in a 3D environment.
  - Shoot energy beams using the repulsor (mouse click).
  - Battle enemies spawned in waves with increasing difficulty.

- **Dynamic Enemy Spawning:**
  - Enemies spawn based on game difficulty (Easy, Medium, Hard).
  - Enemies spawn in waves and increase in number and health as the game progresses.
  
- **Health and Shooting Mechanics:**
  - The player has a health bar, which decreases when hit by enemies and can be replenished.
  - The player shoots energy beams toward the mouse cursor with a cooldown system.

- **3D Environment:**
  - Features a futuristic city map loaded from external files with interactive walls and entities.
  
- **HUD (Heads-Up Display):**
  - Displays the player's health bar, number of enemies killed, and shooting accuracy.
  - Updates in real-time as the game progresses.

- **Game Difficulty and Progression:**
  - Adjust the difficulty and game mechanics such as the number of enemies and their health.
  - Gain health for every 5 enemies killed.

- **Pause and Resume Functionality:**
  - Press `Escape` to pause and resume the game.

- **Customization via External Files:**
  - Select and load custom assets (3D models, sounds) from the user’s file system.

- **Audio Integration:**
  - Includes sound effects such as repulsor firing using the `pygame.mixer`.

- **Exception Logging:**
  - Game errors are logged in a `fps_game.log` file for debugging purposes.

## Requirements

To run the game, you need:

- Python 3.6+
- **Ursina Engine**
- **Pygame** (for sound integration)
- **Panda3D** (for 3D model loading)
