"""
Pytest configuration for VulnScan backend tests.
"""
import sys
import os

# Make sure the backend root is always on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
