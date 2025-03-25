"""
test_openai_client.py

Tests for OpenAI client compatibility with various providers.
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
TEST_API_KEY = os.getenv("TEST_API_KEY", "ddc-CLI67Xo7FQ13CzuHAMhKnF939xncl06Wh4VQLeTvjSh5ZucF5v")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

def list_available_models():
    """List all available models from the API."""
    print_section_header("Listing Available Models")
    try:
        models = client.models.list()
        for model in models:
            print(f"Model ID: {model.id}")
        print("\n")
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return None

def test_non_streaming_completion(model_id, system_message="You are a helpful assistant.", user_message="Hello! Please provide a greeting (non-streaming mode)."):
    """
    Tests non-streaming completion for a given model.
    
    Args:
        model_id (str): The model ID to test
        system_message (str): The system message to use
        user_message (str): The user message to use
        
    Returns:
        object: The response from the API
    """
    print_test_case(f"{model_id} Non-Streaming Completion")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
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

def test_streaming_completion(model_id, system_message="You are a helpful assistant.", user_message="Hello! Please provide a greeting (streaming mode)."):
    """
    Tests streaming completion for a given model.
    
    Args:
        model_id (str): The model ID to test
        system_message (str): The system message to use
        user_message (str): The user message to use
        
    Returns:
        str: The full content of the response
    """
    print_test_case(f"{model_id} Streaming Completion")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
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

def test_provider(provider_name, models):
    """
    Test streaming and non-streaming completions for a specific provider's models.
    
    Args:
        provider_name (str): The provider name (e.g., "Provider-1")
        models (list): List of model names to test for this provider
    """
    print_section_header(f"{provider_name} Testing")
    
    for model in models:
        model_id = f"{provider_name}/{model}"
        
        # Test non-streaming
        test_non_streaming_completion(model_id)
        
        # Test streaming
        test_streaming_completion(model_id)
        
        print_separator()

if __name__ == '__main__':
    # List all available models
    list_available_models()
    
    # Test Provider 1
    test_provider("Provider-1", ["DeepSeek-R1"])
    
    # Test Provider 2
    test_provider("Provider-2", ["gpt-4o"])
    
    # Test Provider 3
    test_provider("Provider-3", ["DeepSeek-R1", "o3-mini"])
    
    # Test Provider 4 (streaming only)
    print_section_header("Provider-4 Testing (Streaming Only)")
    test_streaming_completion("Provider-4/DeepSeek-R1")
    test_streaming_completion("Provider-4/DeepSeek-R1-Distill-Llama-70B")
    test_streaming_completion("Provider-4/DeepSeekV3")
    
    # Test Provider 5
    test_provider("Provider-5", ["gpt-4o"])
    
    # Test Provider 7
    test_provider("Provider-7", ["claude-3.7-sonnet"])
    
    print_section_header("End of All Provider Tests")
