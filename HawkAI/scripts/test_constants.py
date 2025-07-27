#!/usr/bin/env python3

"""
Test script to verify that constants are working correctly
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import constants
from config.constants import (
    PROJECT_ID, 
    LOCATION, 
    MODEL_NAME_FLASH, 
    MODEL_NAME_PRO, 
    BUCKET_NAME, 
    FUNCTION_NAME
)

# Print constants
print("HawkAI Project Constants:")
print(f"PROJECT_ID: {PROJECT_ID}")
print(f"LOCATION: {LOCATION}")
print(f"MODEL_NAME_FLASH: {MODEL_NAME_FLASH}")
print(f"MODEL_NAME_PRO: {MODEL_NAME_PRO}")
print(f"BUCKET_NAME: {BUCKET_NAME}")
print(f"FUNCTION_NAME: {FUNCTION_NAME}")

print("\nConstants imported successfully!")