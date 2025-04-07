#!/usr/bin/env python
"""
Provider_5_Testing.py

A simple test script to verify streaming and non-streaming chat completions
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

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

def print_separator():
    """Prints a separator line for readability."""
    print("\n" + "=" * 80 + "\n")

def test_non_streaming(model_id):
    """Tests non-streaming completion for a given model."""
    print(f"Testing non-streaming completion with model: {model_id}")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
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
        
    except Exception as e:
        print(f"Error during non-streaming test: {e}")

def test_streaming(model_id):
    """Tests streaming completion for a given model."""
    print(f"Testing streaming completion with model: {model_id}")
    
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

if __name__ == "__main__":
    model = "Provider-5/gpt-4o"
    
    print_separator()
    test_non_streaming(model)
    print_separator()
    test_streaming(model)
    print_separator()

# =============================================================================
# SUPPORTED MODELS FOR PROVIDER-5
# =============================================================================
"""
Provider-5/gpt-4o-mini
Provider-5/gpt-4o
Provider-5/o1-mini
Provider-5/qwen-2.5-coder-32b
Provider-5/llama-3.3-70b
Provider-5/deepseek-v3
Provider-5/claude-3.7-sonnet
Provider-5/deepseek-r1-distill-qwen-32b
Provider-5/deepseek-r1
Provider-5/deepseek-r1-llama-70b
Provider-5/gemini-2.0-flash
Provider-5/gemini-2.0-flash-thinking
"""