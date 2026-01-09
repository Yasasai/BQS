"""
Final Quick Populator for BQS. 
Simplified entry point for dummy data generation.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from populate_dummy_data import populate

if __name__ == "__main__":
    populate()
