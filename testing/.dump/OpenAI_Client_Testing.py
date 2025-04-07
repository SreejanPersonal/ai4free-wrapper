#!/usr/bin/env python
"""
OpenAI_Client_Testing.py

A complete test script to verify streaming and non-streaming chat completions 
for all providers using the modern alias naming convention:
  Provider-X/model_name

Tested providers and their models:
  • Provider 1 – DeepSeek-R1 (streaming and non-streaming)
  • Provider 2 – gpt-4o (streaming and non-streaming)
  • Provider 3 – DeepSeek-R1 and o3-mini (streaming and non-streaming)
  • Provider 4 – DeepSeek-R1, DeepSeek-R1-Distill-Llama-70B, and DeepSeekV3 (streaming only)

Before running, ensure that your .env file and centralized data/models.json have been updated accordingly.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TEST_API_KEY = "ddc-CLI67Xo7FQ13CzuHAMhKnF939xncl06Wh4VQLeTvjSh5ZucF5v"  # Replace with your test API key if needed.
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")

# Initialize the OpenAI client with our local API (which supports all providers)
client = OpenAI(
    api_key=TEST_API_KEY,
    base_url=f"{LOCAL_API_URL}/v1"
)

########################################################################
#                             Helper Functions                         #
########################################################################

def print_section_header(title: str):
    """Prints a decorative section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


# ########################################################################
# #                              MAIN TESTING                            #
# ########################################################################

if __name__ == '__main__':

    # List all available models
    print_section_header("Listing Available Models")
    models = client.models.list()
    for model in models:
        # We assume that our models have an attribute 'id'
        print(f"Model ID: {model.id}")
    print("\n")

    ########################################################################
    #                    Provider 1 – DeepSeek-R1 Tests                    #
    ########################################################################
    print_section_header("Provider-1: DeepSeek-R1 Testing")

    # Non-Streaming Test for Provider-1
    print(">> Provider-1 Non-Streaming Completion:")
    non_streaming_completion = client.chat.completions.create(
        model="Provider-1/DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-1."},
            {"role": "user", "content": "Hello! Please provide a greeting (non-streaming mode)."}
        ],
        stream=False
    )
    print(non_streaming_completion.choices[0].message.content)

    # Streaming Test for Provider-1
    print("\n>> Provider-1 Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-1/DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-1."},
            {"role": "user", "content": "Hello! Please provide a greeting (streaming mode)."}
        ],
        stream=True
    )
    for chunk in streaming_completion:
        # Print each chunk's delta content as it arrives
        print(chunk.choices[0].delta.content, end='')
    print("\n" + "-" * 80)

    ########################################################################
    #                   Provider 2 – gpt-4o Tests                          #
    ########################################################################
    print_section_header("Provider-2: gpt-4o Testing")

    # Non-Streaming Test for Provider-2
    print(">> Provider-2 Non-Streaming Completion:")
    non_streaming_completion = client.chat.completions.create(
        model="Provider-2/gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-2."},
            {"role": "user", "content": "Hello! Please provide a greeting (non-streaming mode)."}
        ],
        stream=False
    )
    print(non_streaming_completion.choices[0].message.content)

    # Streaming Test for Provider-2
    print("\n>> Provider-2 Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-2/gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-2."},
            {"role": "user", "content": "Hello! Please provide a greeting (streaming mode)."}
        ],
        stream=True
    )
    for chunk in streaming_completion:
        print(chunk.choices[0].delta.content, end='')
    print("\n" + "-" * 80)

    ########################################################################
    #                 Provider 3 – DeepSeek-R1 Tests                       #
    ########################################################################
    print_section_header("Provider-3: DeepSeek-R1 Testing")

    # Non-Streaming Test for Provider-3 (DeepSeek-R1)
    print(">> Provider-3 (DeepSeek-R1) Non-Streaming Completion:")
    non_streaming_completion = client.chat.completions.create(
        model="Provider-3/DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-3 (DeepSeek-R1)."},
            {"role": "user", "content": "Hello! Provide a greeting (non-streaming mode)."}
        ],
        stream=False
    )
    print(non_streaming_completion.choices[0].message.content)

    # Streaming Test for Provider-3 (DeepSeek-R1)
    print("\n>> Provider-3 (DeepSeek-R1) Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-3/DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-3 (DeepSeek-R1)."},
            {"role": "user", "content": "Hello! Provide a greeting (streaming mode)."}
        ],
        stream=True
    )
    for chunk in streaming_completion:
        print(chunk.choices[0].delta.content, end='')
    print("\n" + "-" * 80)

    ########################################################################
    #                    Provider 3 – o3-mini Tests                        #
    ########################################################################
    print_section_header("Provider-3: o3-mini Testing")

    # Non-Streaming Test for Provider-3 (o3-mini)
    print(">> Provider-3 (o3-mini) Non-Streaming Completion:")
    non_streaming_completion = client.chat.completions.create(
        model="Provider-3/o3-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-3 (o3-mini)."},
            {"role": "user", "content": "Hello! Provide a greeting (non-streaming mode)."}
        ],
        stream=False
    )
    print(non_streaming_completion.choices[0].message.content)

    # Streaming Test for Provider-3 (o3-mini)
    print("\n>> Provider-3 (o3-mini) Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-3/o3-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-3 (o3-mini)."},
            {"role": "user", "content": "Hello! Provide a greeting (streaming mode)."}
        ],
        stream=True
    )
    for chunk in streaming_completion:
        print(chunk.choices[0].delta.content, end='')
    print("\n" + "-" * 80)

    ########################################################################
    #                    Provider 4 – DeepSeek-R1 Tests                    #
    ########################################################################
    print_section_header("Provider-4: DeepSeek-R1 Testing (Streaming Only)")

    # Streaming Test for Provider-4 (DeepSeek-R1)
    print(">> Provider-4 (DeepSeek-R1) Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-4/DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-4."},
            {"role": "user", "content": "Hello! Provide a greeting (streaming mode) for DeepSeek-R1."}
        ],
        stream=True
    )
    try:
        for chunk in streaming_completion:
            print(chunk.choices[0].delta.content, end='')
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "-" * 80)

    ########################################################################
    #              Provider 4 – DeepSeek-R1-Distill-Llama-70B Tests                 #
    ########################################################################
    print_section_header("Provider-4: DeepSeek-R1-Distill-Llama-70B Testing (Streaming Only)")

    # Streaming Test for Provider-4 (DeepSeek-R1-Distill-Llama-70B)
    print(">> Provider-4 (DeepSeek-R1-Distill-Llama-70B) Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-4/DeepSeek-R1-Distill-Llama-70B",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-4."},
            {"role": "user", "content": "Hello! Provide a greeting (streaming mode) for DeepSeek-R1-Distill-Llama-70B."}
        ],
        stream=True
    )
    try:
        for chunk in streaming_completion:
            print(chunk.choices[0].delta.content, end='')
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "-" * 80)

    ########################################################################
    #                   Provider 4 – DeepSeekV3 Tests                      #
    ########################################################################
    print_section_header("Provider-4: DeepSeekV3 Testing (Streaming Only)")

    # Streaming Test for Provider-4 (DeepSeekV3)
    print(">> Provider-4 (DeepSeekV3) Streaming Completion:")
    streaming_completion = client.chat.completions.create(
        model="Provider-4/DeepSeekV3",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from Provider-4."},
            {"role": "user", "content": "Hello! Provide a greeting (streaming mode) for DeepSeekV3."}
        ],
        stream=True
    )
    try:
        for chunk in streaming_completion:
            print(chunk.choices[0].delta.content, end='')
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "=" * 80)
    print("=== End of All Provider Tests ===")