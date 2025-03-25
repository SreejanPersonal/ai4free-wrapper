"""
test_provider_5.py

Tests for Provider 5 chat completions.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# Import helper functions
from testing.utils.test_helpers import print_section_header, print_test_case, print_separator

# Load environment variables
load_dotenv()

# Configuration
TEST_API_KEY = os.getenv("TEST_API_KEY", "ddc-beta-u5gklyo1yv-ecw2CwOvnIrvk2uoyULxs7RtAVcvrXnZRPQ")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

def test_non_streaming(model_id):
    """
    Tests non-streaming completion for a given model.
    
    Args:
        model_id (str): The model ID to test
    """
    print_test_case(f"Non-streaming completion with model: {model_id}")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hi."}
            ],
            stream=False
        )
        
        print("Response received:")
        print(f"Content: {response.choices[0].message.content}")
        if hasattr(response, 'usage'):
            print(f"Usage: {response.usage}")
        print("Non-streaming test completed successfully.")
        
    except Exception as e:
        print(f"Error during non-streaming test: {e}")

def test_streaming(model_id):
    """
    Tests streaming completion for a given model.
    
    Args:
        model_id (str): The model ID to test
    """
    print_test_case(f"Streaming completion with model: {model_id}")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a short paragraph about artificial intelligence."}
            ],
            stream=True
        )
        
        print("Streaming response:")
        full_content = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end="", flush=True)
        
        print("\nStreaming test completed successfully.")
        
    except Exception as e:
        print(f"Error during streaming test: {e}")

def test_provider_5_models():
    """
    Test all supported Provider 5 models.
    """
    # List of supported models for Provider 5
    models = [
        "Provider-5/gpt-4o-mini",
        "Provider-5/gpt-4o",
        "Provider-5/o1-mini",
        "Provider-5/qwen-2.5-coder-32b",
        "Provider-5/llama-3.3-70b",
        "Provider-5/deepseek-v3",
        "Provider-5/claude-3.7-sonnet",
        "Provider-5/deepseek-r1-distill-qwen-32b",
        "Provider-5/deepseek-r1",
        "Provider-5/deepseek-r1-llama-70b",
        "Provider-5/gemini-2.0-flash",
        "Provider-5/gemini-2.0-flash-thinking"
    ]
    
    for model in models:
        print_separator()
        print_section_header(f"Testing {model}")
        
        # Test non-streaming
        test_non_streaming(model)
        
        # Test streaming
        test_streaming(model)

if __name__ == "__main__":
    # Test with a specific model
    model = "Provider-5/gpt-4o"
    
    print_separator()
    print_section_header(f"PROVIDER 5 TESTING: {model}")
    
    test_non_streaming(model)
    print_separator()
    # test_streaming(model)
    # print_separator()
    
    # Uncomment to test all supported models
    # test_provider_5_models()
