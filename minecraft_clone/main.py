#!/usr/bin/env python
"""
Minecraft Clone - Main Game Entry Point
A simple Minecraft-like game built with Python, Pygame, and PyOpenGL.
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from minecraft_clone.engine.game import Game


def main():
    """Main entry point for the Minecraft clone game."""
    # Initialize the game
    game = Game()
    
    # Start the game loop
    try:
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)
    
    # Clean exit
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
