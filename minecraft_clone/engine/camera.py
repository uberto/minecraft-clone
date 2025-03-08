"""
Camera class - Handles the player's view in the 3D world.
"""

import math
import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    """First-person camera for navigating the 3D world."""
    
    def __init__(self, position=None, yaw=-90.0, pitch=0.0):
        """Initialize the camera with position and orientation."""
        # Camera position (x, y, z)
        self.position = np.array(position if position else [0, 0, 0], dtype=np.float32)
        
        # Camera orientation
        self.yaw = yaw  # Horizontal rotation (in degrees)
        self.pitch = pitch  # Vertical rotation (in degrees)
        
        # Camera vectors
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.world_up = np.array([0, 1, 0], dtype=np.float32)
        
        # Camera settings
        self.movement_speed = 5.0  # Units per second
        self.mouse_sensitivity = 0.1  # Degrees per pixel
        
        # Update vectors based on initial angles
        self._update_camera_vectors()
    
    def _update_camera_vectors(self):
        """Calculate the front, right, and up vectors from yaw and pitch."""
        # Calculate new front vector
        front = np.zeros(3, dtype=np.float32)
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        
        # Normalize vectors
        self.front = front / np.linalg.norm(front)
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def process_keyboard(self, keys):
        """Process keyboard input for camera movement."""
        # Forward/backward
        if keys[K_w]:
            self.position += self.front * self.movement_speed * 0.1
        if keys[K_s]:
            self.position -= self.front * self.movement_speed * 0.1
        
        # Left/right
        if keys[K_a]:
            self.position -= self.right * self.movement_speed * 0.1
        if keys[K_d]:
            self.position += self.right * self.movement_speed * 0.1
        
        # Up/down
        if keys[K_SPACE]:
            self.position += self.world_up * self.movement_speed * 0.1
        if keys[K_LSHIFT]:
            self.position -= self.world_up * self.movement_speed * 0.1
    
    def process_mouse_movement(self, dx, dy):
        """Process mouse movement for camera rotation."""
        dx *= self.mouse_sensitivity
        dy *= self.mouse_sensitivity
        
        self.yaw += dx
        self.pitch -= dy  # Reversed since y-coordinates increase downward
        
        # Constrain pitch to avoid flipping
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        # Update camera vectors
        self._update_camera_vectors()
    
    def update(self, dt):
        """Update camera state based on elapsed time."""
        # Currently, all updates are done in process_keyboard and process_mouse_movement
        pass
    
    def apply(self):
        """Apply the camera transformation to the OpenGL modelview matrix."""
        # Calculate the look-at point
        target = self.position + self.front
        
        # Apply the look-at transformation
        gluLookAt(
            self.position[0], self.position[1], self.position[2],  # Camera position
            target[0], target[1], target[2],  # Look-at point
            self.up[0], self.up[1], self.up[2]  # Up vector
        )
