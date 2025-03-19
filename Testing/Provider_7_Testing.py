#!/usr/bin/env python
"""
Provider_7_Testing.py

A simple test script to verify streaming and non-streaming chat completions
for Provider 7 (meow.cablyai.com)
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Easy to change model at the top
MODEL = "Provider-7/claude-3.7-sonnet"

# Configuration
TEST_API_KEY = "ddc-CLI67Xo7FQ13CzuHAMhKnF939xncl06Wh4VQLeTvjSh5ZucF5v"
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Initialize the OpenAI client with our local API
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

models = client.models.list()
for model in models:
    print(model.id)

def print_separator():
    """Prints a separator line for readability."""
    print("\n" + "=" * 80 + "\n")

def test_non_streaming():
    """Tests non-streaming completion."""
    print(f"Testing non-streaming completion with model: {MODEL}")
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
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

def test_streaming():
    """Tests streaming completion."""
    print(f"Testing streaming completion with model: {MODEL}")
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
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
    print_separator()
    print(f"TESTING PROVIDER 7 WITH MODEL: {MODEL}")
    print_separator()
    
    test_non_streaming()
    print_separator()
    test_streaming()
    print_separator()

# =============================================================================
# SUPPORTED MODELS FOR PROVIDER-7
# =============================================================================
"""
Provider-7/gpt-4o
Provider-7/gemini-2.0-flash
Provider-7/gpt-4o-mini
Provider-7/grok-2
Provider-7/command-a
Provider-7/claude-3.5-sonnet
Provider-7/claude-3.5-sonnet-v2
Provider-7/claude-3.7-sonnet
Provider-7/gpt-4.5-preview
Provider-7/gpt-4.5
Provider-7/o1
Provider-7/chatgpt-4o-latest
Provider-7/sonar-pro
Provider-7/grok-3
Provider-7/gpt-4o-mini-search-preview
Provider-7/deepseek-r1
Provider-7/deepseek-v3
"""
