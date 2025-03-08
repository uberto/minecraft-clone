"""
World class - Manages the voxel world, chunks, and terrain generation.
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import noise


class Block:
    """Represents a single block in the world."""
    
    # Block types
    AIR = 0
    GRASS = 1
    DIRT = 2
    STONE = 3
    
    # Block colors (R, G, B)
    COLORS = {
        AIR: (0, 0, 0),  # Transparent
        GRASS: (0.2, 0.8, 0.2),  # Green
        DIRT: (0.6, 0.3, 0.0),  # Brown
        STONE: (0.5, 0.5, 0.5),  # Gray
    }
    
    @staticmethod
    def get_color(block_type):
        """Get the color for a block type."""
        return Block.COLORS.get(block_type, (1, 0, 1))  # Default to magenta for unknown types


class Chunk:
    """A chunk of the world containing multiple blocks."""
    
    def __init__(self, position=(0, 0, 0), size=16):
        """Initialize a chunk with position and size."""
        self.position = position  # (x, y, z) position of chunk in world
        self.size = size  # Size of chunk in each dimension
        
        # Initialize blocks as a 3D array (x, y, z)
        self.blocks = np.zeros((size, size, size), dtype=np.uint8)
        
        # OpenGL display list for rendering
        self.display_list = None
        self.needs_update = True
    
    def set_block(self, x, y, z, block_type):
        """Set a block at the specified position within the chunk."""
        if 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size:
            self.blocks[x, y, z] = block_type
            self.needs_update = True
    
    def get_block(self, x, y, z):
        """Get the block type at the specified position within the chunk."""
        if 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size:
            return self.blocks[x, y, z]
        return Block.AIR  # Return air for out-of-bounds positions
    
    def _is_face_visible(self, x, y, z, dx, dy, dz):
        """Check if a face is visible (adjacent to air or chunk boundary)."""
        nx, ny, nz = x + dx, y + dy, z + dz
        
        # If the adjacent position is outside the chunk, consider it visible
        if not (0 <= nx < self.size and 0 <= ny < self.size and 0 <= nz < self.size):
            # For top faces (dy=1) and side faces at chunk boundaries, make them visible
            if dy == 1 or dx != 0 or dz != 0:
                return True
                
            # For other faces at chunk boundaries, check with the world
            wx = x + self.position[0] * self.size
            wy = y + self.position[1] * self.size
            wz = z + self.position[2] * self.size
            
            # Calculate world coordinates of the adjacent block
            world_nx = wx + dx
            world_ny = wy + dy
            world_nz = wz + dz
            
            # Ask the parent world if this block exists and is air
            # This will be set by the World class when it adds the chunk
            if hasattr(self, 'world'):
                return self.world.get_block(world_nx, world_ny, world_nz) == Block.AIR
            return True
        
        # If the adjacent block is air, the face is visible
        return self.blocks[nx, ny, nz] == Block.AIR
    
    def generate_mesh(self):
        """Generate the mesh for rendering the chunk."""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        # Disable culling temporarily to ensure all faces are rendered
        glDisable(GL_CULL_FACE)
        
        # Iterate through all blocks in the chunk
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    block_type = self.blocks[x, y, z]
                    
                    # Skip air blocks
                    if block_type == Block.AIR:
                        continue
                    
                    # Get block color
                    r, g, b = Block.get_color(block_type)
                    
                    # World position of block
                    wx = x + self.position[0] * self.size
                    wy = y + self.position[1] * self.size
                    wz = z + self.position[2] * self.size
                    
                    # Check each face of the block
                    # Top face (y+1)
                    if self._is_face_visible(x, y, z, 0, 1, 0):
                        glColor3f(r, g, b)
                        glBegin(GL_QUADS)
                        glVertex3f(wx, wy + 1, wz)
                        glVertex3f(wx + 1, wy + 1, wz)
                        glVertex3f(wx + 1, wy + 1, wz + 1)
                        glVertex3f(wx, wy + 1, wz + 1)
                        glEnd()
                    
                    # Bottom face (y-1)
                    if self._is_face_visible(x, y, z, 0, -1, 0):
                        glColor3f(r * 0.8, g * 0.8, b * 0.8)  # Slightly darker
                        glBegin(GL_QUADS)
                        glVertex3f(wx, wy, wz)
                        glVertex3f(wx, wy, wz + 1)
                        glVertex3f(wx + 1, wy, wz + 1)
                        glVertex3f(wx + 1, wy, wz)
                        glEnd()
                    
                    # Front face (z+1)
                    if self._is_face_visible(x, y, z, 0, 0, 1):
                        glColor3f(r * 0.9, g * 0.9, b * 0.9)
                        glBegin(GL_QUADS)
                        glVertex3f(wx, wy, wz + 1)
                        glVertex3f(wx, wy + 1, wz + 1)
                        glVertex3f(wx + 1, wy + 1, wz + 1)
                        glVertex3f(wx + 1, wy, wz + 1)
                        glEnd()
                    
                    # Back face (z-1)
                    if self._is_face_visible(x, y, z, 0, 0, -1):
                        glColor3f(r * 0.9, g * 0.9, b * 0.9)
                        glBegin(GL_QUADS)
                        glVertex3f(wx, wy, wz)
                        glVertex3f(wx + 1, wy, wz)
                        glVertex3f(wx + 1, wy + 1, wz)
                        glVertex3f(wx, wy + 1, wz)
                        glEnd()
                    
                    # Right face (x+1)
                    if self._is_face_visible(x, y, z, 1, 0, 0):
                        glColor3f(r * 0.85, g * 0.85, b * 0.85)
                        glBegin(GL_QUADS)
                        glVertex3f(wx + 1, wy, wz)
                        glVertex3f(wx + 1, wy, wz + 1)
                        glVertex3f(wx + 1, wy + 1, wz + 1)
                        glVertex3f(wx + 1, wy + 1, wz)
                        glEnd()
                    
                    # Left face (x-1)
                    if self._is_face_visible(x, y, z, -1, 0, 0):
                        glColor3f(r * 0.85, g * 0.85, b * 0.85)
                        glBegin(GL_QUADS)
                        glVertex3f(wx, wy, wz)
                        glVertex3f(wx, wy + 1, wz)
                        glVertex3f(wx, wy + 1, wz + 1)
                        glVertex3f(wx, wy, wz + 1)
                        glEnd()
        
        # Re-enable culling after rendering
        glEnable(GL_CULL_FACE)
        
        glEndList()
        self.needs_update = False
    
    def render(self):
        """Render the chunk."""
        if self.needs_update:
            self.generate_mesh()
        
        if self.display_list is not None:
            glCallList(self.display_list)


class World:
    """Manages the voxel world, including chunks and terrain generation."""
    
    def __init__(self, world_size=4):
        """Initialize the world with a specified size."""
        self.world_size = world_size  # Number of chunks in each horizontal dimension
        self.chunk_size = 16  # Size of each chunk
        self.height = 2  # Number of chunks in vertical dimension
        
        # Dictionary to store chunks, keyed by position (x, y, z)
        self.chunks = {}
        
        # Set camera starting position higher to see the terrain better
        self.camera_start_height = 30
        
        # Generate the initial world
        self._generate_world()
    
    def _generate_world(self):
        """Generate the initial world with terrain."""
        # Create chunks
        for x in range(-self.world_size // 2, self.world_size // 2):
            for z in range(-self.world_size // 2, self.world_size // 2):
                for y in range(self.height):
                    chunk = Chunk(position=(x, y, z), size=self.chunk_size)
                    # Set a reference to the world for chunk boundary checks
                    chunk.world = self
                    self.chunks[(x, y, z)] = chunk
        
        # Generate terrain
        self._generate_terrain()
    
    def _generate_terrain(self):
        """Generate terrain using Perlin noise."""
        # Noise parameters
        scale = 20.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        seed = 42  # Fixed seed for reproducibility
        
        # Generate heightmap
        for chunk_x in range(-self.world_size // 2, self.world_size // 2):
            for chunk_z in range(-self.world_size // 2, self.world_size // 2):
                # Process each column in the chunk
                for x in range(self.chunk_size):
                    for z in range(self.chunk_size):
                        # Calculate world coordinates
                        world_x = chunk_x * self.chunk_size + x
                        world_z = chunk_z * self.chunk_size + z
                        
                        # Generate height using Perlin noise
                        nx = world_x / scale
                        nz = world_z / scale
                        height_value = noise.pnoise2(nx, nz, octaves=octaves, 
                                                    persistence=persistence, 
                                                    lacunarity=lacunarity, 
                                                    repeatx=1024, 
                                                    repeaty=1024, 
                                                    base=seed)
                        
                        # Scale height to chunk coordinates
                        height = int((height_value + 1) * 10) + 16  # Range 6-26
                        # Ensure height is at least 1 to avoid completely flat terrain
                        height = max(height, 1)
                        
                        # Fill in blocks
                        for chunk_y in range(self.height):
                            chunk = self.chunks.get((chunk_x, chunk_y, chunk_z))
                            if chunk is None:
                                continue
                            
                            for y in range(self.chunk_size):
                                # Calculate world y coordinate
                                world_y = chunk_y * self.chunk_size + y
                                
                                # Determine block type based on height
                                if world_y < height - 4:
                                    block_type = Block.STONE
                                elif world_y < height - 1:
                                    block_type = Block.DIRT
                                elif world_y < height:
                                    block_type = Block.GRASS
                                else:
                                    block_type = Block.AIR
                                
                                # Set the block
                                chunk.set_block(x, y, z, block_type)
    
    def get_chunk(self, x, y, z):
        """Get the chunk at the specified position."""
        return self.chunks.get((x, y, z))
    
    def get_block(self, x, y, z):
        """Get the block at the specified world position."""
        # Convert world coordinates to chunk coordinates
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        chunk_z = z // self.chunk_size
        
        # Get the chunk
        chunk = self.get_chunk(chunk_x, chunk_y, chunk_z)
        if chunk is None:
            return Block.AIR
        
        # Convert world coordinates to local chunk coordinates
        local_x = x % self.chunk_size
        local_y = y % self.chunk_size
        local_z = z % self.chunk_size
        
        # Get the block
        return chunk.get_block(local_x, local_y, local_z)
    
    def set_block(self, x, y, z, block_type):
        """Set the block at the specified world position."""
        # Convert world coordinates to chunk coordinates
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        chunk_z = z // self.chunk_size
        
        # Get the chunk
        chunk = self.get_chunk(chunk_x, chunk_y, chunk_z)
        if chunk is None:
            return
        
        # Convert world coordinates to local chunk coordinates
        local_x = x % self.chunk_size
        local_y = y % self.chunk_size
        local_z = z % self.chunk_size
        
        # Set the block
        chunk.set_block(local_x, local_y, local_z, block_type)
    
    def update(self, dt):
        """Update the world state."""
        # Currently, the world is static, so no updates are needed
        pass
    
    def render(self):
        """Render all chunks in the world."""
        for chunk in self.chunks.values():
            chunk.render()
