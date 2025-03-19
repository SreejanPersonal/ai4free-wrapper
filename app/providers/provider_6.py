import base64
import logging
import os
import random
import time
from typing import List, Optional, Union
import requests

from .base_provider import BaseProvider
from ..config import Config

log = logging.getLogger(__name__)

class Provider6(BaseProvider):
    """
    Provider 6 implementation for image generation.
    
    Model aliases are:
      • "Provider-6/flux-schnell" → maps to internal model name
      • "Provider-6/flux-dev"     → maps to internal model name
      • "Provider-6/sana-6b"      → maps to internal model name
    """

    def __init__(self):
        # Get API endpoint from environment variables
        self.api_endpoint = os.getenv("PROVIDER_6_BASE_URL")
        if not self.api_endpoint:
            log.warning("PROVIDER_6_BASE_URL not set in environment variables")
        
        # Map our model aliases to provider's actual model names
        self.alias_to_actual = {
            "Provider-6/flux-schnell": "flux_1_schnell",
            "Provider-6/flux-dev": "flux_1_dev",
            "Provider-6/sana-6b": "sana_1_6b"
        }
        
        self.models = self._load_models()

    def _get_random_user_agent(self):
        """Generate a random user agent string for API requests"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        return random.choice(user_agents)

    def _load_models(self):
        """Loads the model information from models.json for Provider 6 image generation models."""
        try:
            models = []
            # Get all models from Config
            all_models = Config.ALLOWED_MODELS
            
            # Filter models for this provider
            for model in all_models:
                if model['id'].startswith("Provider-6/"):
                    # Create model entry with data from models.json
                    model_entry = {
                        "id": model['id'],
                        "description": model.get('description', f"{model['id'].split('/')[-1]} model"),
                        "max_tokens": 1000,  # Not applicable for image models but needed for consistency
                        "provider": "Provider-6",
                        "owner_cost_per_million_tokens": model.get('owner_cost_per_million_tokens', 6.00),
                        "type": model.get('type', 'image')  # All Provider-6 models are image models
                    }
                    models.append(model_entry)
            
            return models
        except Exception as e:
            log.error(f"Error loading models for Provider 6: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs) -> dict:
        """
        This provider only supports image generation, not chat completion.
        Implementing this method to satisfy the BaseProvider interface.
        """
        raise NotImplementedError("Provider6 only supports image generation, not chat completion")

    def image_generation(self, prompt: str, size: str = "1024x1024", n: int = 1, 
                      response_format: str = "url", model: str = "Provider-6/flux-schnell", **kwargs):
        """
        Generates images using Provider 6 API with an OpenAI-compatible interface.
        
        Args:
            prompt (str): The prompt to generate the image from
            size (str): Image size (not directly used by Provider 6 but mapped to aspect ratio)
            n (int): Number of images to generate
            response_format (str): Format of the response. Can be "url" or "b64_json"
            model (str): Model to use (default is "Provider-6/flux-schnell")
                
        Returns:
            Dictionary with a timestamp and image data in OpenAI-compatible format
        """
        # Map the model name to provider's actual model name
        if model not in self.alias_to_actual:
            log.warning(f"Model '{model}' not found in Provider 6 models, using default")
            actual_model = "model_variant_1"  # Default model
        else:
            actual_model = self.alias_to_actual[model]
        
        # Map size to Provider 6 aspect ratio format
        # Provider 6 uses "1_1" format for square images
        size_mapping = {
            "1024x1024": "1_1",  # Square
            "1024x1792": "9_16",  # Portrait
            "1792x1024": "16_9",  # Landscape
        }
        
        # Default to 1_1 if size not in mapping
        aspect_ratio = size_mapping.get(size, "1_1")
        
        # Prepare headers for the API request
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://fastflux.co",
            "referer": "https://fastflux.co/",
            "user-agent": self._get_random_user_agent()
        }
        
        # Prepare payload for the API request
        payload = {
            "prompt": prompt,
            "model": actual_model,
            "size": aspect_ratio,
            "isPublic": False  # Set to False for privacy
        }
        
        # Initialize result
        result = {
            "created": int(time.time()),
            "data": []
        }
        
        try:
            # Generate n images
            for i in range(n):
                # Make the API request
                try:
                    log.info(f"Sending request to Provider 6 API: {self.api_endpoint}")
                    log.debug(f"Payload: {payload}")
                    
                    response = requests.post(
                        self.api_endpoint,
                        json=payload,
                        headers=headers,
                    )
                    
                    # Check for successful response
                    response.raise_for_status()
                    log.info(f"Provider 6 API response status: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    log.error(f"Provider 6 API request failed: {e}")
                    raise Exception(f"Provider 6 API connection error: {e}")
                
                # Parse the response
                response_data = response.json()
                
                if response_data and 'result' in response_data:
                    # Get base64 data and remove header
                    image_data = response_data['result']
                    # The result is in format "data:image/png;base64,BASE64_DATA"
                    # Extract just the base64 part
                    base64_data = image_data.split(',')[1]
                    
                    # Add to result based on requested format
                    if response_format == "b64_json":
                        result["data"].append({"b64_json": base64_data})
                    else:  # Default to "url" format
                        # For URL format, return a data URL
                        result["data"].append({"url": image_data})  # Use the full data URL
                else:
                    raise Exception("Invalid response format from Provider 6 API")
            
            return result
                
        except Exception as e:
            log.error(f"Error in Provider6 image_generation: {e}")
            raise

    def get_models(self) -> list:
        """Returns the list of supported models for Provider6."""
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens for the given model."""
        for model in self.models:
            if model["id"] == model_id:
                return model["max_tokens"]
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS

    def get_default_max_tokens(self, model_id: str) -> int:
        """Returns the default maximum generation tokens for the given model."""
        for model in self.models:
            if model["id"] == model_id:
                return Config.get_model_config(model_id, {}).get("max_output_tokens", Config.MAX_OUTPUT_TOKENS)
        return Config.MAX_OUTPUT_TOKENS
