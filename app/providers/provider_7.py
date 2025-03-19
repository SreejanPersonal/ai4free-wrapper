import requests
import json
import time
import logging
import os
from dotenv import load_dotenv; load_dotenv()
from ..utils.token_counter import count_tokens
from ..config import Config
from . import BaseProvider

log = logging.getLogger(__name__)

class MaxAPIKeyRotationsError(Exception):
    """Exception raised when all API keys have been tried and failed."""
    pass

class Provider7(BaseProvider):
    """
    Provider 7 implementation.
    This provider uses the OpenAI-compatible API at meow.cablyai.com.
    
    Features:
    - Supports multiple API keys with automatic rotation on errors
    - Configurable error codes that trigger rotation
    - Prevents infinite rotation loops by tracking rotation count
    
    Configuration:
    - PROVIDER_7_API_KEYS: JSON array of API keys
    - PROVIDER_7_ERROR_CODES: JSON array of status codes that trigger rotation, or ["*"] for all errors
    """
    # Class variables to track API key rotation
    _current_key_index = 0
    _rotation_count = 0

    def __init__(self):
        self.models = self._load_models()
        self.base_url = os.environ.get("PROVIDER_7_BASE_URL", "https://meow.cablyai.com/v1")
        
        # Support for multiple API keys
        api_keys_str = os.environ.get("PROVIDER_7_API_KEYS", "[]")
        self.api_keys = json.loads(api_keys_str) if api_keys_str else []
        
        # Fallback to single API key if no list is provided
        if not self.api_keys:
            single_key = os.environ.get("PROVIDER_7_API_KEY", "")
            if single_key:
                self.api_keys = [single_key]
        
        # Error codes that should trigger API key rotation
        error_codes_str = os.environ.get("PROVIDER_7_ERROR_CODES", "[429]")
        self.error_codes = json.loads(error_codes_str) if error_codes_str else [429]
        
        # Set current API key
        self.current_api_key = self.api_keys[self._current_key_index] if self.api_keys else ""
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.current_api_key}"
        }
        
        # Log the initial API key being used
        if self.api_keys:
            log.info(f"Provider 7 initialized with API key #{Provider7._current_key_index + 1}/{len(self.api_keys)}: {self._mask_api_key(self.current_api_key)}")

    def _load_models(self):
        """Loads the model information from the centralized file."""
        try:
            models = []
            for model_data in Config.ALLOWED_MODELS:
                if model_data.get("id", "").startswith("Provider-7/"):
                    models.append({
                        "id": model_data["id"],
                        "description": model_data.get("description", ""),
                        "max_tokens": (Config.get_model_config(model_data["id"])["max_input_tokens"] +
                                      Config.get_model_config(model_data["id"])["max_output_tokens"]),
                        "provider": "Provider-7",
                        "owner_cost_per_million_tokens": model_data.get("owner_cost_per_million_tokens", 0)
                    })
            return models
        except Exception as e:
            log.error(f"Error loading models for Provider7: {e}")
            return []

    def _generate_fake_id(self):
        """Generate a dummy unique identifier for the chat completion."""
        return str(int(time.time() * 1000))

    def _mask_api_key(self, api_key):
        """Mask API key for logging purposes, showing only first 8 and last 4 characters."""
        if not api_key or len(api_key) < 12:
            return "****"
        return f"{api_key[:8]}...{api_key[-4:]}"
        
    def _should_rotate_key(self, status_code):
        """
        Determine if API key rotation should be triggered based on error code.
        
        Args:
            status_code: HTTP status code from the failed request
            
        Returns:
            bool: True if key rotation should be triggered, False otherwise
        """
        # Wildcard means rotate on any error
        if "*" in self.error_codes:
            return True
        
        # Check if specific status code should trigger rotation
        return status_code in self.error_codes
    
    def _rotate_api_key(self, error_info=""):
        """
        Rotate to the next API key in the list.
        
        Args:
            error_info: Information about the error that triggered rotation
            
        Raises:
            MaxAPIKeyRotationsError: If all keys have been tried and failed
        """
        if not self.api_keys:
            raise MaxAPIKeyRotationsError("No API keys available for rotation")
        
        # Log the current key that failed
        current_key_num = Provider7._current_key_index + 1
        masked_key = self._mask_api_key(self.current_api_key)
        log.warning(f"API key #{current_key_num}/{len(self.api_keys)} ({masked_key}) failed: {error_info}")
            
        # Increment rotation count
        Provider7._rotation_count += 1
        
        # Check if we've tried all keys
        if Provider7._rotation_count > len(self.api_keys):
            # Reset rotation count
            Provider7._rotation_count = 0
            raise MaxAPIKeyRotationsError("All API keys have been tried and failed")
        
        # Move to next key
        Provider7._current_key_index = (Provider7._current_key_index + 1) % len(self.api_keys)
        self.current_api_key = self.api_keys[Provider7._current_key_index]
        
        # Update authorization header
        self.headers["Authorization"] = f"Bearer {self.current_api_key}"
        
        # Log the new key being used
        new_key_num = Provider7._current_key_index + 1
        masked_new_key = self._mask_api_key(self.current_api_key)
        log.info(f"Rotated to API key #{new_key_num}/{len(self.api_keys)}: {masked_new_key}")

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """
        Performs a chat completion using the meow.cablyai.com API.
        With automatic API key rotation on specified errors.
        """
        # Extract model name without the provider prefix
        actual_model = model_id.split("/", 1)[1] if "/" in model_id else model_id
        
        # Prepare the payload
        payload = {
            "model": actual_model,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters if provided
        for param in ["temperature", "top_p", "presence_penalty", "frequency_penalty", "max_tokens"]:
            if param in kwargs and kwargs[param] is not None:
                payload[param] = kwargs[param]
        
        endpoint = f"{self.base_url}/chat/completions"
        
        while True:  # Keep trying until success or all keys fail
            try:
                if stream:
                    # For streaming responses
                    response = requests.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload, 
                        stream=True
                    )
                    
                    if response.status_code != 200:
                        # Check if we should rotate key
                        if self._should_rotate_key(response.status_code):
                            error_info = f"Status {response.status_code}"
                            self._rotate_api_key(error_info)
                            continue  # Try again with new key
                        else:
                            log.error(f"Provider 7 API error: Status {response.status_code}, Response: {response.text}")
                            raise Exception(f"Provider 7 API error: Status {response.status_code}, Detail: {response.text}")
                    
                    # Reset rotation count on success
                    Provider7._rotation_count = 0
                    
                    def generate():
                        for line in response.iter_lines():
                            if line:
                                # Remove the "data: " prefix if present
                                line_text = line.decode('utf-8')
                                if line_text.startswith("data: "):
                                    data = line_text[6:]
                                    
                                    # Check for the end of the stream
                                    if data == "[DONE]":
                                        continue
                                    
                                    try:
                                        # Parse the JSON data
                                        chunk = json.loads(data)
                                        yield chunk
                                    except json.JSONDecodeError as e:
                                        log.error(f"Error decoding JSON: {e}")
                                        continue
                    
                    return generate()
                else:
                    # For non-streaming responses
                    response = requests.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload
                    )
                    
                    if response.status_code != 200:
                        # Check if we should rotate key
                        if self._should_rotate_key(response.status_code):
                            error_info = f"Status {response.status_code}"
                            self._rotate_api_key(error_info)
                            continue  # Try again with new key
                        else:
                            log.error(f"Provider 7 API error: Status {response.status_code}, Response: {response.text}")
                            raise Exception(f"Provider 7 API error: Status {response.status_code}, Detail: {response.text}")
                    
                    # Reset rotation count on success
                    Provider7._rotation_count = 0
                    
                    # Parse the response
                    response_data = response.json()
                    
                    # Calculate token usage if not provided by the API
                    if not response_data.get("usage"):
                        completion_content = response_data["choices"][0]["message"]["content"]
                        completion_tokens = count_tokens(
                            [{"role": "assistant", "content": completion_content}],
                            model_id,
                            kwargs.get('app')
                        )
                        prompt_tokens = count_tokens(messages, model_id, kwargs.get('app'))
                        total_tokens = prompt_tokens + completion_tokens
                        
                        response_data["usage"] = {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens
                        }
                    
                    return response_data
                    
            except MaxAPIKeyRotationsError as e:
                # All keys failed, propagate the error
                log.error(f"All API keys failed: {e}")
                raise
            except Exception as e:
                # For other exceptions, try to rotate if it's a connection error
                if isinstance(e, requests.exceptions.RequestException):
                    try:
                        error_info = f"Connection error: {str(e)[:100]}"
                        self._rotate_api_key(error_info)
                        continue  # Try again with new key
                    except MaxAPIKeyRotationsError as max_err:
                        log.error(f"All API keys failed: {max_err}")
                        raise
                
                # Other errors are propagated
                log.error(f"Error in Provider 7 chat completion: {e}")
                raise

    def get_models(self) -> list:
        """Returns the supported models information for Provider 7."""
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens supported by the given model."""
        for model in self.models:
            if model["id"] == model_id:
                return model["max_tokens"]
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS

    def get_default_max_tokens(self, model_id: str) -> int:
        """Get the default maximum generation tokens for the given model."""
        for model in self.models:
            if model["id"] == model_id:
                return Config.get_model_config(model_id)["max_output_tokens"]
        return Config.MAX_OUTPUT_TOKENS
