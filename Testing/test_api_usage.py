import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")  # Default if not set
# LOCAL_API_URL = "https://beta.sree.shop"
USAGE_ENDPOINT = f"{LOCAL_API_URL}/usage"

def test_api_usage(api_key):
    """
    Tests the usage API endpoint by sending a POST request with the given API key
    and prints out the returned usage details.
    """
    payload = {
        "api_key": api_key
    }
    try:
        response = requests.post(USAGE_ENDPOINT, json=payload)
        response.raise_for_status()  # Raise an error on bad status

        # Parse and print the returned usage details
        data = response.json()
        print("Usage details received:")
        print(json.dumps(data, indent=2))
        return data

    except requests.exceptions.RequestException as e:
        print(f"API usage test failed: {e}")
        return None

if __name__ == '__main__':
    # Replace with your current API key
    test_api_key = "ddc-EcAsBdRXr20WbkSwvcyAxeS6SvHLzVOBxGPsbM3Bu5U8RMQIqw"
    test_api_usage(test_api_key)