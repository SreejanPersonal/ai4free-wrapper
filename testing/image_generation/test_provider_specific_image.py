"""
test_provider_specific_image.py

Tests for provider-specific image generation functionality.
"""

import os
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
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

def test_provider_3_image_generation():
    """Test the image generation functionality with Provider 3's flux-1.1-ultra model."""
    print_section_header("Testing Image Generation with Provider 3")
    
    output_dir = create_output_directory("output/images/provider3")
    
    # Test with URL format (default)
    try:
        print_test_case("Provider 3 - URL format")
        response = client.images.generate(
            model="Provider-3/flux-1.1-ultra", 
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
            filename = f"{output_dir}/provider3_url_format.jpg"
            save_image(image_url, filename)
    
    except Exception as e:
        print(f"Error during Provider 3 URL format test: {e}")
    
    # Test with b64_json format
    try:
        print_test_case("Provider 3 - b64_json format")
        response = client.images.generate(
            model="Provider-3/flux-1.1-ultra",
            prompt="A futuristic city with flying cars",
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
            filename = f"{output_dir}/provider3_b64_format.jpg"
            save_image(image_b64, filename)
    
    except Exception as e:
        print(f"Error during Provider 3 b64_json format test: {e}")

def test_provider_6_image_generation():
    """Test the Provider 6 image generation functionality."""
    print_section_header("Testing Provider 6 Image Generation")
    
    # Set test mode for Provider 6
    os.environ["PROVIDER_6_TEST_MODE"] = "true"
    
    output_dir = create_output_directory("output/images/provider6")
    
    # Test all three Provider 6 models
    models = [
        "Provider-6/flux-schnell",
        "Provider-6/flux-dev",
        "Provider-6/sana-6b"
    ]
    
    for model in models:
        # Test with URL format (default)
        try:
            print_test_case(f"{model} - URL format")
            response = client.images.generate(
                model=model,
                prompt="A beautiful mountain landscape with a sunset",
                n=1,
                size="1024x1024"
            )
            
            print("URL Format Response received:")
            print(f"Created: {response.created}")
            print(f"Data count: {len(response.data)}")
            
            # Save the first image
            if response.data:
                image_url = response.data[0].url
                print(f"Image URL: {image_url[:50]}...") # Print just the beginning
                model_name = model.split('/')[-1]
                filename = f"{output_dir}/{model_name}_url.jpg"
                save_image(image_url, filename)
        
        except Exception as e:
            print(f"Error during URL format test for {model}: {e}")
        
        # Test with b64_json format
        try:
            print_test_case(f"{model} - b64_json format")
            response = client.images.generate(
                model=model,
                prompt="A cyberpunk city at night with neon lights",
                n=1,
                size="1024x1024",
                response_format="b64_json"
            )
            
            print("b64_json Format Response received:")
            print(f"Created: {response.created}")
            print(f"Data count: {len(response.data)}")
            
            # Save the first image
            if response.data:
                image_b64 = response.data[0].b64_json
                print(f"Image b64: {image_b64[:50]}...") # Print just the beginning
                model_name = model.split('/')[-1]
                filename = f"{output_dir}/{model_name}_b64.jpg"
                save_image(image_b64, filename)
        
        except Exception as e:
            print(f"Error during b64_json format test for {model}: {e}")

if __name__ == "__main__":
    # Test Provider 3 image generation
    test_provider_3_image_generation()
    
    # Test Provider 6 image generation
    test_provider_6_image_generation()
