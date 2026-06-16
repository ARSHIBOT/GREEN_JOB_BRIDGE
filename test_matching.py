import unittest
import numpy as np
import sys
import os

# Append the directory to import app functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import cosine_similarity_calc

class TestSemanticMatching(unittest.TestCase):
    def test_identical_vectors(self):
        """Test that identical vectors return a similarity of 1.0."""
        vec = [1, 2, 3]
        score = cosine_similarity_calc(vec, vec)
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_orthogonal_vectors(self):
        """Test that orthogonal (perpendicular) vectors return 0.0."""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        score = cosine_similarity_calc(vec1, vec2)
        self.assertAlmostEqual(score, 0.0, places=5)

    def test_opposite_vectors(self):
        """Test that opposite vectors return -1.0."""
        vec1 = [1, 2, 3]
        vec2 = [-1, -2, -3]
        score = cosine_similarity_calc(vec1, vec2)
        self.assertAlmostEqual(score, -1.0, places=5)

    def test_zero_vector(self):
        """Test that handles a zero vector gracefully (returns 0.0)."""
        vec1 = [0, 0, 0]
        vec2 = [1, 2, 3]
        score = cosine_similarity_calc(vec1, vec2)
        self.assertEqual(score, 0.0)

    def test_vector_normalization(self):
        """Test that magnitude of vectors does not affect similarity."""
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]  # Multiplied by 2
        score = cosine_similarity_calc(vec1, vec2)
        self.assertAlmostEqual(score, 1.0, places=5)

if __name__ == '__main__':
    unittest.main()
