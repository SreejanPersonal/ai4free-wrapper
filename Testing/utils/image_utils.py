"""
image_utils.py

Utility functions for handling images in test scripts.
"""

import base64
import os

def save_image(image_data, filename="generated_image.jpg"):
    """
    Save a base64-encoded image to a file.
    
    Args:
        image_data (str): Base64-encoded image data or URL
        filename (str): Name of the file to save the image to
    """
    # If the image_data is a data URL, extract just the base64 part
    if image_data.startswith("data:image"):
        image_data = image_data.split(",")[1]
    
    # Decode and save
    image_bytes = base64.b64decode(image_data)
    with open(filename, 'wb') as file:
        file.write(image_bytes)
    print(f'Image saved to {filename}')

def create_output_directory(directory="output"):
    """
    Creates a directory for saving test outputs if it doesn't exist.
    
    Args:
        directory (str): The directory name to create
    
    Returns:
        str: The path to the created directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created output directory: {directory}")
    return directory
