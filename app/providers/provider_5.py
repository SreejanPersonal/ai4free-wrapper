import requests
import json
import random
import base64
import time
import logging
import os
from dotenv import load_dotenv
from .base_provider import BaseProvider
from ..config import Config

log = logging.getLogger(__name__)
load_dotenv()

class Provider5(BaseProvider):
    """
    This provider supports both streaming and non-streaming completions
    with various models through a unified interface.
    """

    def __init__(self):
        self.api_key = os.environ.get("PROVIDER_5_API_KEY")
        self.base_url = os.environ.get("PROVIDER_5_BASE_URL")
        self.endpoint = f"{self.base_url}/openai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.alias_to_actual = {
            "Provider-5/gpt-4o-mini": "openai",
            "Provider-5/gpt-4o": "openai-large",
            "Provider-5/o1-mini": "openai-reasoning",
            "Provider-5/qwen-2.5-coder-32b": "qwen-coder",
            "Provider-5/llama-3.3-70b": "llama",
            "Provider-5/deepseek-v3": "deepseek",
            "Provider-5/claude-3.7-sonnet": "claude",
            "Provider-5/deepseek-r1-distill-qwen-32b": "deepseek-r1",
            "Provider-5/deepseek-r1": "deepseek-reasoner",
            "Provider-5/deepseek-r1-llama-70b": "deepseek-r1-llama",
            "Provider-5/gemini-2.0-flash": "gemini",
            "Provider-5/gemini-2.0-flash-thinking": "gemini-thinking"
        }
        
        self.models = self._load_models()

    def _load_models(self):
        """Loads the model information based on our alias mapping."""
        try:
            models = []
            # Get all models from Config
            all_models = Config.ALLOWED_MODELS
            
            for alias, actual_model in self.alias_to_actual.items():
                # Get model configuration from Config
                model_config = Config.get_model_config(alias)
                
                # Find the matching model in ALLOWED_MODELS to get the correct pricing
                model_pricing = 0.50  # Default fallback
                for model in all_models:
                    if model['id'] == alias:
                        model_pricing = model.get('owner_cost_per_million_tokens', 0.50)
                        break
                
                # Extract the model name from the alias for the description
                model_name = alias.split("/")[1]
                
                # Create model entry with the correct pricing
                model_entry = {
                    "id": alias,
                    "description": f"{model_name} model",
                    "max_tokens": (model_config["max_input_tokens"] + 
                                model_config["max_output_tokens"]),
                    "provider": "Provider-5",
                    "owner_cost_per_million_tokens": model_pricing
                }
                models.append(model_entry)
            return models
        except Exception as e:
            log.error(f"Error loading models for Provider5: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """        
        This method handles both streaming and non-streaming requests.
        """
        # Check if the model is supported
        if model_id not in self.alias_to_actual:
            raise ValueError(f"Model '{model_id}' is not supported by Provider5")
        
        actual_model = self.alias_to_actual[model_id]
        
        # Prepare the request payload
        payload = {
            "model": actual_model,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters if provided
        for param in ["temperature", "max_tokens", "top_p", "presence_penalty", "frequency_penalty"]:
            if param in kwargs:
                payload[param] = kwargs[param]
        
        try:
            # Make the API request
            response = requests.post(
                self.endpoint, 
                headers=self.headers, 
                json=payload,
                stream=stream
            )
            
            # Check for successful response
            if response.status_code != 200:
                log.error(f"Provider 5 API error: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Provider 5 API error: Status {response.status_code}, Detail: {response.text}")
            
            # Handle streaming response
            if stream:
                def generate():
                    for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                        if not line:
                            continue
                        data_str = line[len("data:"):].strip() if line.startswith("data:") else line.strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            yield chunk
                        except json.JSONDecodeError as e:
                            log.error(f"JSON parsing error in stream: {e}")
                            continue
                return generate()
            
            # Handle non-streaming response
            else:
                return response.json()
                
        except Exception as e:
            log.error(f"Error in Provider5 chat_completion: {e}")
            raise

    def image_generation(self, prompt: str, size: str = "1024x1024", n: int = 1, 
                     response_format: str = "url", model: str = "flux", **kwargs):
        """
        Generates images using Provider 5's image generation API with an OpenAI-compatible interface.
        
        Args:
            prompt (str): The prompt to generate the image from
            size (str): Image size in format "widthxheight", e.g. "1024x1024"
            n (int): Number of images to generate (only returns first one in this implementation)
            response_format (str): Format of the response. Can be "url" or "b64_json"
            model (str): Model to use (default is "flux")
            
        Returns:
            Dictionary with a timestamp and image data in OpenAI-compatible format
        """
        # Map the model names to Provider 5's actual model names
        model_mapping = {
            "flux-pro": "flux",
            "flux-schnell": "turbo"
        }
        
        actual_model = model_mapping.get(model, "flux")  # Default to flux if model not found
        
        # Parse size parameter
        try:
            width, height = map(int, size.split("x"))
        except ValueError:
            width, height = 1024, 1024  # Default to 1024x1024 if parsing fails
        
        # Generate a random seed for variety
        seed = random.randint(1, 10000)
        
        # Build the API URL with supported parameters
        base_url = os.environ.get('PROVIDER_5_IMG_BASE_URL')
        api_url = f"{base_url}/{prompt}?width={width}&height={height}&model={actual_model}&seed={seed}&nologo=true&nofeed=yes"
        
        try:
            # Download the image
            response = requests.get(api_url)
            
            # Check if the response was successful
            if response.status_code != 200:
                log.error(f"Provider 5 image generation API error: Status {response.status_code}")
                raise Exception(f"Provider 5 image generation API error: Status {response.status_code}")
            
            # Convert the image to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            
            # Create a timestamp
            timestamp = int(time.time())
            
            # Create the response in OpenAI-compatible format
            result = {
                "created": timestamp,
                "data": []
            }
            
            # Generate n images (though we're using the same image n times in this implementation)
            for _ in range(n):
                if response_format == "b64_json":
                    result["data"].append({"b64_json": image_data})
                else:  # Default to "url" format
                    result["data"].append({"url": f"data:image/jpeg;base64,{image_data}"})
            
            return result
            
        except Exception as e:
            log.error(f"Error in Provider5 image_generation: {e}")
            raise

    def get_models(self) -> list:
        """Returns the list of supported models for Provider5."""
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
                return Config.get_model_config(model_id)["max_output_tokens"]
        return Config.MAX_OUTPUT_TOKENS