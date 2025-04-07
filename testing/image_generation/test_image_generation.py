"""
test_image_generation.py

General tests for image generation functionality.
"""

import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
import sys
sys.path.append('../..')  # Add parent directory to path for imports
from testing.utils.test_helpers import print_section_header, print_test_case
from testing.utils.image_utils import save_image, create_output_directory

# Load environment variables
load_dotenv()

# Configuration
TEST_API_KEY = os.getenv("TEST_API_KEY", "ddc-CLI67Xo7FQ13CzuHAMhKnF939xncl06Wh4VQLeTvjSh5ZucF5v")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:80")

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

def test_url_format_image_generation(model="Provider-5/flux-schnell", prompt="A beautiful mountain landscape with a sunset"):
    """
    Test image generation with URL format response.
    
    Args:
        model (str): The model to use for image generation
        prompt (str): The prompt to generate an image from
    """
    print_section_header(f"Testing Image Generation - URL format with {model}")
    
    output_dir = create_output_directory("output/images")
    
    try:
        response = client.images.generate(
            model=model, 
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        print("Response received:")
        print(f"Created: {response.created}")
        print(f"Data count: {len(response.data)}")
        
        # Save the first image
        if response.data:
            image_url = response.data[0].url
            print(f"Image URL: {image_url[:50]}...") # Print just the beginning
            filename = f"{output_dir}/{model.replace('/', '_')}_url_format.jpg"
            save_image(image_url, filename)
    
    except Exception as e:
        print(f"Error during URL format test: {e}")

def test_b64_format_image_generation(model="Provider-5/flux-pro", prompt="A futuristic city with flying cars"):
    """
    Test image generation with b64_json format response.
    
    Args:
        model (str): The model to use for image generation
        prompt (str): The prompt to generate an image from
    """
    print_section_header(f"Testing Image Generation - b64_json format with {model}")
    
    output_dir = create_output_directory("output/images")
    
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="b64_json"
        )
        
        print("Response received:")
        print(f"Created: {response.created}")
        print(f"Data count: {len(response.data)}")
        
        # Save the first image
        if response.data:
            image_b64 = response.data[0].b64_json
            print(f"Image b64: {image_b64[:50]}...") # Print just the beginning
            filename = f"{output_dir}/{model.replace('/', '_')}_b64_format.jpg"
            save_image(image_b64, filename)
    
    except Exception as e:
        print(f"Error during b64_json format test: {e}")

def test_multiple_images(model="Provider-5/flux-pro", prompt="A serene lake surrounded by mountains", n=2):
    """
    Test generating multiple images with a single request.
    
    Args:
        model (str): The model to use for image generation
        prompt (str): The prompt to generate images from
        n (int): The number of images to generate
    """
    print_section_header(f"Testing Multiple Image Generation ({n} images) with {model}")
    
    output_dir = create_output_directory("output/images")
    
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size="512x512",
            response_format="b64_json"
        )
        
        print("Response received:")
        print(f"Created: {response.created}")
        print(f"Data count: {len(response.data)}")
        
        # Save all images
        for i, image_data in enumerate(response.data):
            image_b64 = image_data.b64_json
            print(f"Image {i+1} b64: {image_b64[:50]}...") # Print just the beginning
            filename = f"{output_dir}/{model.replace('/', '_')}_multi_{i+1}.jpg"
            save_image(image_b64, filename)
    
    except Exception as e:
        print(f"Error during multiple image generation test: {e}")

if __name__ == "__main__":
    # Test URL format image generation
    test_url_format_image_generation()
    
    # Test b64_json format image generation
    test_b64_format_image_generation()
    
    # Test multiple image generation
    test_multiple_images()
