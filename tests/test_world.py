"""
Unit tests for the world module.
Tests the face visibility logic for blocks in the world.
"""

import unittest
import numpy as np
from minecraft_clone.engine.world import Block, Chunk, World


class TestChunkFaceVisibility(unittest.TestCase):
    """Test the face visibility logic in the Chunk class."""
    
    def setUp(self):
        """Set up a test chunk with a simple block configuration."""
        self.chunk = Chunk(position=(0, 0, 0), size=16)
        
        # Create a simple terrain: a 3x3 platform at y=8 with a single block on top
        for x in range(7, 10):
            for z in range(7, 10):
                # Bottom layer (y=8) - all grass
                self.chunk.set_block(x, 8, z, Block.GRASS)
                
        # Add a single block on top to test top face visibility
        self.chunk.set_block(8, 9, 8, Block.STONE)
        
        # Create a world and link the chunk to it
        self.world = World(world_size=1)
        self.chunk.world = self.world
    
    def test_top_face_visibility(self):
        """Test that top faces are correctly identified as visible."""
        # Test top face of the platform blocks
        for x in range(7, 10):
            for z in range(7, 10):
                if x == 8 and z == 8:
                    # The center block has a stone block above it, so its top face should NOT be visible
                    self.assertFalse(self.chunk._is_face_visible(x, 8, z, 0, 1, 0), 
                                    f"Top face at ({x}, 8, {z}) should NOT be visible")
                else:
                    # All other blocks have air above them, so their top faces should be visible
                    self.assertTrue(self.chunk._is_face_visible(x, 8, z, 0, 1, 0), 
                                   f"Top face at ({x}, 8, {z}) should be visible")
        
        # The top block should have its top face visible (air above)
        self.assertTrue(self.chunk._is_face_visible(8, 9, 8, 0, 1, 0), 
                       "Top face of the stone block should be visible")
    
    def test_side_face_visibility(self):
        """Test that side faces are correctly identified as visible."""
        # Test the center stone block's side faces
        # All 4 sides should be visible (air around)
        self.assertTrue(self.chunk._is_face_visible(8, 9, 8, 1, 0, 0), "Right face should be visible")
        self.assertTrue(self.chunk._is_face_visible(8, 9, 8, -1, 0, 0), "Left face should be visible")
        self.assertTrue(self.chunk._is_face_visible(8, 9, 8, 0, 0, 1), "Front face should be visible")
        self.assertTrue(self.chunk._is_face_visible(8, 9, 8, 0, 0, -1), "Back face should be visible")
        
        # Test the grass block at the edge of the platform
        # This block is at position (8, 8, 7) which is at the edge of our 3x3 platform
        # The block at (8, 8, 8) is the center grass block with a stone block above it
        
        # For this test, we need to clear the block at (8, 8, 8) to make it air
        # so that the front face of (8, 8, 7) is visible
        original_block = self.chunk.get_block(8, 8, 8)
        self.chunk.set_block(8, 8, 8, Block.AIR)
        
        # Now the front face should be visible
        self.assertTrue(self.chunk._is_face_visible(8, 8, 7, 0, 0, 1), "Front face should be visible")
        
        # Restore the original block
        self.chunk.set_block(8, 8, 8, original_block)
        
        # Test that a face adjacent to another block is not visible
        self.assertFalse(self.chunk._is_face_visible(8, 8, 8, 0, 0, -1), "Back face should NOT be visible")
    
    def test_chunk_boundary_visibility(self):
        """Test face visibility at chunk boundaries."""
        # Test blocks at the edge of the chunk
        edge_x, edge_y, edge_z = 15, 8, 15
        self.chunk.set_block(edge_x, edge_y, edge_z, Block.GRASS)
        
        # Faces pointing outside the chunk should be visible
        self.assertTrue(self.chunk._is_face_visible(edge_x, edge_y, edge_z, 1, 0, 0), 
                       "Face at chunk boundary should be visible")
        self.assertTrue(self.chunk._is_face_visible(edge_x, edge_y, edge_z, 0, 0, 1), 
                       "Face at chunk boundary should be visible")
        
        # Top face should always be visible at chunk boundaries
        self.assertTrue(self.chunk._is_face_visible(edge_x, edge_y, edge_z, 0, 1, 0), 
                       "Top face at chunk boundary should be visible")


class TestWorldIntegration(unittest.TestCase):
    """Test the integration between World and Chunk classes."""
    
    def setUp(self):
        """Set up a test world with a simple configuration."""
        self.world = World(world_size=2)
        
        # Clear the world and create a simple flat terrain
        self.world.chunks = {}
        
        # Create a single chunk
        self.chunk = Chunk(position=(0, 0, 0), size=16)
        self.chunk.world = self.world
        self.world.chunks[(0, 0, 0)] = self.chunk
        
        # Add a flat surface of grass blocks at y=8
        for x in range(16):
            for z in range(16):
                self.chunk.set_block(x, 8, z, Block.GRASS)
    
    def test_world_block_access(self):
        """Test that the world can correctly access blocks in chunks."""
        # Check a block that exists
        self.assertEqual(self.world.get_block(8, 8, 8), Block.GRASS, 
                        "Should return GRASS for an existing block")
        
        # Check a block that doesn't exist (air)
        self.assertEqual(self.world.get_block(8, 9, 8), Block.AIR, 
                        "Should return AIR for a non-existent block")
        
        # Check a block outside the chunk
        self.assertEqual(self.world.get_block(20, 8, 20), Block.AIR, 
                        "Should return AIR for a block outside any chunk")
    
    def test_top_face_rendering(self):
        """Test that top faces are correctly identified for rendering."""
        # Force the chunk to regenerate its mesh
        self.chunk.needs_update = True
        
        # Count the number of visible top faces in the chunk
        top_face_count = 0
        for x in range(16):
            for z in range(16):
                if self.chunk._is_face_visible(x, 8, z, 0, 1, 0):
                    top_face_count += 1
        
        # All 256 (16x16) grass blocks should have visible top faces
        self.assertEqual(top_face_count, 256, 
                        "All grass blocks should have visible top faces")


if __name__ == "__main__":
    unittest.main()
