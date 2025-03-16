import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

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

def print_section_header(title: str):
    """Prints a decorative section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

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

def test_image_generation():
    """Test the image generation functionality."""
    print_section_header("Testing Image Generation - URL format")
    
    # Test with URL format (default)
    try:
        response = client.images.generate(
            model="flux-pro", 
            prompt="A beautiful mountain landscape with a sunset",
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
            save_image(image_url, "url_format_image.jpg")
    
    except Exception as e:
        print(f"Error during URL format test: {e}")
    
    print_section_header("Testing Image Generation - b64_json format")
    
    # Test with b64_json format
    try:
        response = client.images.generate(
            model="flux-pro",
            prompt="A futuristic city with flying cars",
            n=2,
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
            save_image(image_b64, "b64_format_image.jpg")
    
    except Exception as e:
        print(f"Error during b64_json format test: {e}")

if __name__ == "__main__":
    test_image_generation()