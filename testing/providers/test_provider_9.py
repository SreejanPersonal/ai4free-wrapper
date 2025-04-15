"""
test_provider_9.py

Simple test script for Provider 9 (Azure OpenAI) chat completions via the local API endpoint.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# Import helper functions (optional, but good for consistent output)
try:
    from testing.utils.test_helpers import print_section_header, print_test_case, print_separator
except ImportError:
    def print_section_header(text): print(f"\n--- {text} ---")
    def print_test_case(text): print(f"\n>>> {text}")
    def print_separator(): print("-" * 40)

load_dotenv()

TEST_API_KEY = os.getenv("TEST_API_KEY", "ddc-beta-u5gklyo1yv-ecw2CwOvnIrvk2uoyULxs7RtAVcvrXnZRPQ")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000") # Your local API endpoint

client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

MODEL_ID = "Provider-9/gpt-4.1"

def test_non_streaming(model_id=MODEL_ID):
    """Tests non-streaming completion."""
    print_test_case(f"Non-streaming test for: {model_id}")
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are an Azure test assistant."},
                {"role": "user", "content": "Say 'Hello from Azure test!'"}
            ],
            stream=False,
            max_tokens=50
        )
        log.info("Non-streaming response received:")
        print(f"Content: {response.choices[0].message.content}")
        if hasattr(response, 'usage'):
            print(f"Usage: {response.usage}")
        print("Non-streaming test completed successfully.")
    except Exception as e:
        log.error(f"Error during non-streaming test for {model_id}: {e}", exc_info=True)
        print(f"Error: {e}")

def test_streaming(model_id=MODEL_ID):
    """Tests streaming completion."""
    print_test_case(f"Streaming test for: {model_id}")
    try:
        response_stream = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are an Azure test assistant."},
                {"role": "user", "content": "Write a very long sentence about testing."}
            ],
            stream=True,
            max_tokens=500
        )
        log.info("Streaming response:")
        full_content = ""
        print("Streamed Content: ", end="")
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end="", flush=True)

        print("\nStreaming finished.")
        log.info(f"Full streamed content: {full_content}")
        print("Streaming test completed successfully.")
    except Exception as e:
        log.error(f"Error during streaming test for {model_id}: {e}", exc_info=True)
        print(f"Error: {e}")

if __name__ == "__main__":
    print_separator()
    print_section_header(f"PROVIDER 9 (Azure) TEST: {MODEL_ID}")

    test_non_streaming()
    print_separator()

    test_streaming()
    print_separator()

    print("Provider 9 tests finished.")
