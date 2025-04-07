import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

load_dotenv()

# Configuration
TEST_API_KEY = os.getenv("TEST_API_KEY", "ddc-beta-u5gklyo1yv-ecw2CwOvnIrvk2uoyULxs7RtAVcvrXnZRPQ") 
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000") 
# Use a valid external model ID from the updated Provider 8 list
TEST_MODEL_ID = "Provider-8/claude-3.7-sonnet:thinking" 

# Initialize Client
try:
    client = OpenAI(
        api_key=TEST_API_KEY,
        base_url=f"{LOCAL_API_URL}/v1" 
    )
except Exception as e:
    print(f"FATAL: Error initializing OpenAI client: {e}")
    sys.exit(1) # Exit if client can't be initialized

def test_non_streaming():
    print(f"\n--- Test: Non-Streaming ({TEST_MODEL_ID}) ---")
    messages = [{"role": "user", "content": "How many r are there in `Strrawberry`? What is your Knowledge cut off ??"}]
    try:
        response = client.chat.completions.create(
            model=TEST_MODEL_ID,
            messages=messages,
            stream=False,
            temperature=0.1
        )
        print(f"Response Content: {response.choices[0].message.content}")
        assert response.choices[0].message.content is not None
        print("Non-Streaming Test: PASSED")
    except Exception as e:
        print(f"Non-Streaming Test: FAILED ({e})")
        assert False # Ensure test runner sees failure

if __name__ == "__main__":
    print(f"Starting Provider 8 Test (API: {LOCAL_API_URL})")
    test_non_streaming()
    print("\nProvider 8 Test Finished.")
