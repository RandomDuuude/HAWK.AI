#!/usr/bin/env python3

"""
Test script to verify image processing functionality
"""

import base64
import io
from PIL import Image
import sys

def test_image_processing():
    # Create a simple test image
    print("Creating test image...")
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    print(f"Base64 image data (first 50 chars): {img_base64[:50]}...")
    
    # Simulate processing
    print("\nProcessing image...")
    try:
        # Decode base64
        image_bytes = base64.b64decode(img_base64)
        
        # Create image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        print(f"Image format: {image.format}, Size: {image.size}, Mode: {image.mode}")
        
        # Process image (resize)
        max_size = (50, 50)  # Smaller for test
        image.thumbnail(max_size, Image.LANCZOS)
        print(f"Resized image size: {image.size}")
        
        # Save processed image to bytes
        processed_byte_arr = io.BytesIO()
        image.save(processed_byte_arr, format='JPEG')
        
        # Convert back to base64
        processed_base64 = base64.b64encode(processed_byte_arr.getvalue()).decode('utf-8')
        print(f"Processed base64 (first 50 chars): {processed_base64[:50]}...")
        
        print("\n✅ Image processing test successful!")
        return True
    except Exception as e:
        print(f"\n❌ Error processing image: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== HawkAI Image Processing Test ===\n")
    success = test_image_processing()
    sys.exit(0 if success else 1)