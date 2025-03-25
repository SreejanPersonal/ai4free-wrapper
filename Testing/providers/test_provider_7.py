"""
test_provider_7.py

Tests for Provider 7 chat completions.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
sys.path.append('../..')  # Add parent directory to path for imports
from testing.utils.test_helpers import print_section_header, print_test_case, print_separator

# Load environment variables
load_dotenv()

# Configuration
TEST_API_KEY = "ddc-beta-ihjmpiwf98-HFrY7hd3BjLU9q8hEgKLEjHuAeQEnhvVPiB"
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Model to test (easy to change at the top)
DEFAULT_MODEL = "Provider-7/claude-3.7-sonnet"

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

def test_non_streaming(model=DEFAULT_MODEL):
    """
    Tests non-streaming completion.
    
    Args:
        model (str): The model ID to test
    """
    print_test_case(f"Non-streaming completion with model: {model}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a short paragraph about artificial intelligence."}
            ],
            stream=False
        )
        
        print("Response received:")
        print(f"Content: {response.choices[0].message.content}")
        if hasattr(response, 'usage'):
            print(f"Usage: {response.usage}")
        print("Non-streaming test completed successfully.")
        return response
        
    except Exception as e:
        print(f"Error during non-streaming test: {e}")
        return None

def test_streaming(model=DEFAULT_MODEL):
    """
    Tests streaming completion.
    
    Args:
        model (str): The model ID to test
    """
    print_test_case(f"Streaming completion with model: {model}")
    
    try:
        response = client.chat.completions.create(
            model=model,
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
        return full_content
        
    except Exception as e:
        print(f"Error during streaming test: {e}")
        return None

def list_models():
    """List all available models from the API."""
    try:
        models = client.models.list()
        provider7_models = [model.id for model in models if model.id.startswith("Provider-7")]
        return provider7_models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def test_provider_7_models():
    """
    Test all supported Provider 7 models.
    """
    # List of supported models for Provider 7
    models = [
        "Provider-7/gpt-4o",
        "Provider-7/gemini-2.0-flash",
        "Provider-7/gpt-4o-mini",
        "Provider-7/grok-2",
        "Provider-7/command-a",
        "Provider-7/claude-3.5-sonnet",
        "Provider-7/claude-3.5-sonnet-v2",
        "Provider-7/claude-3.7-sonnet",
        "Provider-7/gpt-4.5-preview",
        "Provider-7/gpt-4.5",
        "Provider-7/o1",
        "Provider-7/chatgpt-4o-latest",
        "Provider-7/sonar-pro",
        "Provider-7/grok-3",
        "Provider-7/gpt-4o-mini-search-preview",
        "Provider-7/deepseek-r1",
        "Provider-7/deepseek-v3"
    ]
    
    for model in models:
        print_separator()
        print_section_header(f"Testing {model}")
        
        # Test non-streaming
        test_non_streaming(model)
        
        # Test streaming
        test_streaming(model)

if __name__ == "__main__":
    print_separator()
    print_section_header(f"TESTING PROVIDER 7 WITH MODEL: {DEFAULT_MODEL}")
    print_separator()
    
    # Test non-streaming
    test_non_streaming()
    print_separator()
    
    # Test streaming
    test_streaming()
    print_separator()
    
    # Uncomment to list all available Provider 7 models
    # models = list_models()
    # print("Available Provider 7 models:")
    # for model in models:
    #     print(f"- {model}")
    
    # Uncomment to test all supported models
    # test_provider_7_models()
