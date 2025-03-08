"""
Game class - Main game engine for the Minecraft clone.
Handles the game loop, rendering, and input processing.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from minecraft_clone.engine.camera import Camera
from minecraft_clone.engine.world import World


class Game:
    """Main game class that manages the game loop and components."""
    
    def __init__(self, width=800, height=600, title="Minecraft Clone"):
        """Initialize the game with window dimensions and title."""
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode(
            (width, height),
            pygame.DOUBLEBUF | pygame.OPENGL
        )
        pygame.display.set_caption(title)
        
        # Set up the clock for managing frame rate
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Set up OpenGL
        self._setup_opengl()
        
        # Create game components
        self.camera = Camera(position=[0, 10, 10])
        self.world = World()
        
        # Game state
        self.wireframe_mode = False
    
    def _setup_opengl(self):
        """Configure OpenGL settings."""
        # Set up perspective
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 1000.0)
        
        # Set up model view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        
        # Enable backface culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Set clear color (sky blue)
        glClearColor(0.5, 0.7, 1.0, 1.0)
    
    def handle_events(self):
        """Process all game events."""
        for event in pygame.event.get():
            # Quit event
            if event.type == pygame.QUIT:
                self.running = False
            
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                # Escape key to exit
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Toggle wireframe mode with F key
                elif event.key == pygame.K_f:
                    self.wireframe_mode = not self.wireframe_mode
                    if self.wireframe_mode:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                    else:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Continuous key presses for movement
        keys = pygame.key.get_pressed()
        self.camera.process_keyboard(keys)
        
        # Mouse movement for looking around
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        self.camera.process_mouse_movement(mouse_dx, mouse_dy)
    
    def update(self, dt):
        """Update game state."""
        # Update camera
        self.camera.update(dt)
        
        # Update world (if needed)
        self.world.update(dt)
    
    def render(self):
        """Render the game scene."""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up the camera view
        glLoadIdentity()
        self.camera.apply()
        
        # Render the world
        self.world.render()
        
        # Swap the buffers to display what we just rendered
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        # Center mouse and hide cursor
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.running = True
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
        
        # Release mouse when game ends
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
