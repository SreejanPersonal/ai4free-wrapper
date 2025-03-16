import logging
from openai import OpenAI
from .base_provider import BaseProvider
from ..config import Config
import os
import requests
import json
import time
import base64
from dotenv import load_dotenv; load_dotenv()

log = logging.getLogger(__name__)

class Provider3(BaseProvider):
    """
    Provider 3 implementation.
    Originally supports the models "deepseek-r1" and "o3-mini".
    Now also supports "flux-1.1-ultra" for image generation using TypeGPT's Image-Generator.
    
    Model aliases are:
      • "Provider-3/DeepSeek-R1"  → maps to original "deepseek-r1"
      • "Provider-3/o3-mini"      → maps to original "o3-mini"
      • "Provider-3/flux-1.1-ultra" → maps to TypeGPT's "Image-Generator"
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.environ.get("PROVIDER_3_BASE_URL"), 
            api_key=os.environ.get("PROVIDER_3_API_KEY")
        )
        self.typegpt_api_key = os.environ.get("PROVIDER_3_API_KEY")
        self.typegpt_base_url = os.environ.get("PROVIDER_3_BASE_URL")
        
        self.alias_to_actual = {
            "Provider-3/DeepSeek-R1": "deepseek-r1",
            "Provider-3/o3-mini": "o3-mini",
            "Provider-3/flux-1.1-ultra": "flux"  # New mapping for image generation
        }
        self.models = self._load_models()

    def _load_models(self):
        """Creates the models list using the predefined alias mapping."""
        try:
            # Build model entries using our alias-to-actual mappings.
            return [
                {
                    "id": "Provider-3/DeepSeek-R1",
                    "description": "Deepseek Model provided via Provider3",
                    "max_tokens": (Config.get_model_config("Provider-3/DeepSeek-R1")["max_input_tokens"] +
                                   Config.get_model_config("Provider-3/DeepSeek-R1")["max_output_tokens"]),
                    "provider": "Provider-3",
                    "owner_cost_per_million_tokens": 2.00
                },
                {
                    "id": "Provider-3/o3-mini",
                    "description": ("OpenAI's o3-mini: a cost-effective, fast reasoning model "
                                    "with excellent STEM and coding capabilities."),
                    "max_tokens": (Config.get_model_config("Provider-3/o3-mini")["max_input_tokens"] +
                                   Config.get_model_config("Provider-3/o3-mini")["max_output_tokens"]),
                    "provider": "Provider-3",
                    "owner_cost_per_million_tokens": 4.40
                },
                {
                    "id": "Provider-3/flux-1.1-ultra",
                    "description": "High-quality image generation model for creating detailed visuals from text prompts.",
                    "max_tokens": 1000,  # Not really applicable for image models, but needed for consistency
                    "provider": "Provider-3",
                    "owner_cost_per_million_tokens": 8.00,  # Set appropriate cost for image generation
                    "type": "image"  # Mark this as an image model
                }
            ]
        except Exception as e:
            log.error(f"Error loading models for Provider3: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs) -> dict:
        """
        Performs a chat completion.
        Maps the alias to the original model name before calling.
        """
        actual_model = self.alias_to_actual.get(model_id, model_id)
        kwargs.pop('app', None)  # Remove any unwanted keys
        
        try:
            completion = self.client.chat.completions.create(
                model=actual_model,
                messages=messages,
                stream=stream,
                **kwargs
            )
            if stream:
                return completion  # Already a generator for streaming responses
            else:
                return completion.model_dump()  # Non-streaming response as a dict
        except Exception as e:
            log.error(f"Provider 3 API error: {e}")
            raise

    def image_generation(self, prompt: str, size: str = "1024x1024", n: int = 1, 
                     response_format: str = "url", model: str = "Provider-3/flux-1.1-ultra", **kwargs):
        """
        Generates images using TypeGPT's Image-Generator API with an OpenAI-compatible interface.
        
        Args:
            prompt (str): The prompt to generate the image from
            size (str): Image size (not used by TypeGPT but kept for compatibility)
            n (int): Number of images to generate (only returns first one in this implementation)
            response_format (str): Format of the response. Can be "url" or "b64_json"
            model (str): Should be mapped to "Image-Generator" internally
                
        Returns:
            Dictionary with a timestamp and image data in OpenAI-compatible format
        """
        url = f"{self.typegpt_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.typegpt_api_key}",
            "Content-Type": "application/json"
        }
        
        # We always use "Image-Generator" as the actual model for TypeGPT
        data = {
            "model": "flux",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            # Check for successful status code
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                # Extract URL using a simple split logic for efficiency
                image_url = content.split('(')[-1].strip(')')
                
                # Download the image from the URL
                img_response = requests.get(image_url)
                if img_response.status_code != 200:
                    raise Exception(f"Failed to download image from URL: {img_response.status_code}")
                
                # Convert image to base64
                image_b64 = base64.b64encode(img_response.content).decode('utf-8')
                
                # Create timestamp
                timestamp = int(time.time())
                
                # Return data in the requested format
                result = {
                    "created": timestamp,
                    "data": []
                }
                
                # Generate n images (though we're using the same image n times in this implementation)
                for _ in range(n):
                    if response_format == "b64_json":
                        result["data"].append({"b64_json": image_b64})
                    else:  # Default to "url" format
                        result["data"].append({"url": f"data:image/jpeg;base64,{image_b64}"})
                
                return result
            else:
                log.error(f"TypeGPT API error: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"TypeGPT API error: Status {response.status_code}, Detail: {response.text}")
                
        except Exception as e:
            log.error(f"Error in Provider3 image_generation: {e}")
            raise

    def get_models(self) -> list:
        """Returns Provider 3 models (with aliases)."""
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        for model in self.models:
            if model["id"] == model_id:
                return model["max_tokens"]
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS

    def get_default_max_tokens(self, model_id: str) -> int:
        for model in self.models:
            if model["id"] == model_id:
                return Config.get_model_config(model_id)["max_output_tokens"]
        return Config.MAX_OUTPUT_TOKENS