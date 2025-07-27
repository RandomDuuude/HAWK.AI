#!/usr/bin/env python3

"""
Script to extract constants from config/constants.py for use in shell scripts
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import constants
from config.constants import PROJECT_ID, LOCATION, FUNCTION_NAME

# Output constants in a format that can be sourced by shell scripts
print(f"PROJECT_ID=\"{PROJECT_ID}\"")
print(f"LOCATION=\"{LOCATION}\"")
print(f"FUNCTION_NAME=\"{FUNCTION_NAME}\"")