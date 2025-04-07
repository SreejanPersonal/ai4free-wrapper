"""
test_provider_5_audio.py

Tests for Provider 5 audio model.
"""

import os
import base64
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

def test_audio_model():
    """
    Tests the audio model capabilities.
    """
    model_id = "Provider-5/gpt-4o-audio-preview"
    print_test_case(f"Audio generation with model: {model_id}")
    
    try:
        # We need to pass audio parameters as extra_body parameters since they're not standard parameters
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Is a golden retriever a good family dog?"}
            ],
            extra_body={
                "modalities": ["text", "audio"],
                "audio": {"voice": "alloy", "format": "wav"}
            }
        )
        
        print("Response received:")
        print(f"Content: {response.choices[0].message.content}")
        
        # Check if audio data is present in the response
        if hasattr(response.choices[0].message, 'audio') and hasattr(response.choices[0].message.audio, 'data'):
            # Save the audio file
            audio_data = response.choices[0].message.audio.data
            wav_bytes = base64.b64decode(audio_data)
            with open("audio_response_test.wav", "wb") as f:
                f.write(wav_bytes)
            print("Audio data saved to audio_response_test.wav")
        else:
            print("No audio data in response")
            
        print("Audio model test completed successfully.")
        
    except Exception as e:
        print(f"Error during audio model test: {e}")

if __name__ == "__main__":
    print_separator()
    print_section_header("PROVIDER 5 AUDIO MODEL TESTING")
    
    test_audio_model()
    print_separator()
