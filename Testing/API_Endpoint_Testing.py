# test_api.py
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")  # Default if not set
# LOCAL_API_URL = "https://beta.sree.shop"
SYSTEM_SECRET = os.getenv("SYSTEM_SECRET")

def generate_api_key(user_id, telegram_user_link, first_name="Test", last_name="User", username="test_user"):
    """Generates a new API key for testing."""
    try:
        response = requests.post(
            f"{LOCAL_API_URL}/v1/api-keys",
            json={
                'secret': SYSTEM_SECRET,
                'user_id': user_id,
                'telegram_user_link': telegram_user_link,
                'first_name': first_name,
                'last_name': last_name,
                'username': username
            }
        )

        if response.status_code == 409: 
            print(response.json())
            return None
        
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        api_key = response.json()['api_key']
        print("Generated API Key:", api_key)
        return api_key
    except requests.exceptions.RequestException as e:
        print(f"Key generation failed: {e}")
        return None

def test_list_models(api_key):
    """Tests listing available models."""
    try:
        response = requests.get(
            f"{LOCAL_API_URL}/v1/models",
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        models = response.json()
        print("Available Models:", json.dumps(models, indent=2))  # Pretty print JSON
        return models
    except requests.exceptions.RequestException as e:
        print(f"Models listing failed: {e}")
        return None

def test_chat_completion(api_key, model_id, message_content, stream=False):
    """Tests a chat completion request (both streaming and non-streaming)."""
    try:
        response = requests.post(
            f"{LOCAL_API_URL}/v1/chat/completions",
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'model': model_id,
                'messages': [{'role': 'user', 'content': message_content}],
                'stream': stream
            }
        )
        response.raise_for_status()

        if stream:
            print(f"Streaming response (model: {model_id}):")
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):  # Stream by chunks
                print(chunk, end="")  # Print each chunk as it arrives
            print("\nEnd of streaming response.")
        else:
            completion = response.json()
            print(f"Chat completion (model: {model_id}):", json.dumps(completion, indent=2)) # Pretty Print
            return completion

    except requests.exceptions.RequestException as e:
        print(f"Chat completion failed: {e}")
        return None

def test_rate_limit(api_key, model_id):
    """Tests the rate limiting (sends multiple requests quickly)."""
    print("Testing rate limiting...")
    for i in range(15):  # Send more requests than the limit
        print(f"  Request {i + 1}")
        test_chat_completion(api_key, model_id, "Say 'hello'")

if __name__ == '__main__':
    # 1. Generate an API key (you can run this part once, then comment it out)
    api_key = generate_api_key("test_user_124", "tg://user?id=1234567890")
    # api_key = "ddc-cGZh5j5Cf8udpaBnBQjNaYGc2teXdVFZkxcozxYQbXYBH55zL7"
    # print("API Key:", api_key)
    
    if not api_key:
        print("API key generation failed.  Exiting.")
        exit()

    # 2. List models
    # test_list_models(api_key)

    # 3. Test chat completion (non-streaming)
    # test_chat_completion(api_key, "deepseek-ai/DeepSeek-R1", "Just Say HI")
    # test_chat_completion(api_key, "gpt-4o", "Just Say HI.")

    # # # 4. Test chat completion (streaming)
    # test_chat_completion(api_key, "deepseek-ai/DeepSeek-R1", "Write a short story about a cat.", stream=True)
    # test_chat_completion(api_key, "gpt-4o", "Just Day Hi", stream=True)

    # # 5. Test rate limiting
    # test_rate_limit(api_key, "deepseek-ai/DeepSeek-R1")  # Use a valid model ID