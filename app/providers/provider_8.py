import requests
import json
import os
import logging
from dotenv import load_dotenv
from .base_provider import BaseProvider
from ..config import Config
from ..utils.token_counter import count_tokens # Import for potential future use

log = logging.getLogger(__name__)
load_dotenv()

class Provider8(BaseProvider):
    """
    Provider 8: An OpenAI-compatible provider.
    Focuses on direct response streaming without intermediate parsing.
    """

    def __init__(self):
        self.api_key = os.environ.get("PROVIDER_8_API_KEY")
        self.base_url = os.environ.get("PROVIDER_8_BASE_URL")

        self.endpoint = f"{self.base_url}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Mapping from external ID (Provider-8/model-name) to internal API ID (provider/model-name)
        self.alias_to_actual = {
            "Provider-8/llama-4-maverick:free": "meta-llama/llama-4-maverick:free",
            "Provider-8/llama-4-maverick": "meta-llama/llama-4-maverick",
            "Provider-8/llama-4-scout:free": "meta-llama/llama-4-scout:free",
            "Provider-8/llama-4-scout": "meta-llama/llama-4-scout",
            "Provider-8/gemini-2.5-pro-preview-03-25": "google/gemini-2.5-pro-preview-03-25",
            "Provider-8/quasar-alpha": "openrouter/quasar-alpha",
            "Provider-8/deepseek-v3-base:free": "deepseek/deepseek-v3-base:free",
            "Provider-8/deepseek-chat-v3-0324:free": "deepseek/deepseek-chat-v3-0324:free",
            "Provider-8/deepseek-chat-v3-0324": "deepseek/deepseek-chat-v3-0324",
            "Provider-8/o1-pro": "openai/o1-pro",
            "Provider-8/command-a": "cohere/command-a",
            "Provider-8/gpt-4o-mini-search-preview": "openai/gpt-4o-mini-search-preview",
            "Provider-8/gpt-4o-search-preview": "openai/gpt-4o-search-preview",
            "Provider-8/sonar-reasoning-pro": "perplexity/sonar-reasoning-pro",
            "Provider-8/sonar-reasoning": "perplexity/sonar-reasoning",
            "Provider-8/sonar-pro": "perplexity/sonar-pro",
            "Provider-8/gpt-4.5-preview": "openai/gpt-4.5-preview",
            "Provider-8/gemini-2.0-flash-lite-001": "google/gemini-2.0-flash-lite-001",
            "Provider-8/claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
            "Provider-8/claude-3.7-sonnet:thinking": "anthropic/claude-3.7-sonnet:thinking",
            "Provider-8/claude-3.7-sonnet:beta": "anthropic/claude-3.7-sonnet:beta",
            "Provider-8/o3-mini-high": "openai/o3-mini-high",
            "Provider-8/gemini-2.0-flash-001": "google/gemini-2.0-flash-001",
            "Provider-8/gemini-2.0-pro-exp-02-05:free": "google/gemini-2.0-pro-exp-02-05:free",
            "Provider-8/o3-mini": "openai/o3-mini",
            "Provider-8/gemini-2.0-flash-thinking-exp:free": "google/gemini-2.0-flash-thinking-exp:free",
            "Provider-8/deepseek-r1:free": "deepseek/deepseek-r1:free",
            "Provider-8/deepseek-r1": "deepseek/deepseek-r1",
            "Provider-8/grok-2-vision-1212": "x-ai/grok-2-vision-1212",
            "Provider-8/grok-2-1212": "x-ai/grok-2-1212",
            "Provider-8/claude-3.5-haiku:beta": "anthropic/claude-3.5-haiku:beta",
            "Provider-8/claude-3.5-haiku": "anthropic/claude-3.5-haiku",
            "Provider-8/claude-3.5-haiku-20241022:beta": "anthropic/claude-3.5-haiku-20241022:beta",
            "Provider-8/claude-3.5-haiku-20241022": "anthropic/claude-3.5-haiku-20241022",
            "Provider-8/claude-3.5-sonnet:beta": "anthropic/claude-3.5-sonnet:beta",
            "Provider-8/claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
            "Provider-8/o1-preview": "openai/o1-preview",
            "Provider-8/o1-preview-2024-09-12": "openai/o1-preview-2024-09-12",
            "Provider-8/o1-mini": "openai/o1-mini",
            "Provider-8/o1-mini-2024-09-12": "openai/o1-mini-2024-09-12",
            "Provider-8/chatgpt-4o-latest": "openai/chatgpt-4o-latest",
            "Provider-8/gpt-4o-2024-08-06": "openai/gpt-4o-2024-08-06",
            "Provider-8/gpt-4o-mini": "openai/gpt-4o-mini",
            "Provider-8/gpt-4o-mini-2024-07-18": "openai/gpt-4o-mini-2024-07-18",
            "Provider-8/claude-3.5-sonnet-20240620:beta": "anthropic/claude-3.5-sonnet-20240620:beta",
            "Provider-8/claude-3.5-sonnet-20240620": "anthropic/claude-3.5-sonnet-20240620",
            "Provider-8/gemini-flash-1.5": "google/gemini-flash-1.5",
            "Provider-8/gpt-4o": "openai/gpt-4o",
            "Provider-8/gpt-4o:extended": "openai/gpt-4o:extended",
            "Provider-8/gpt-4o-2024-05-13": "openai/gpt-4o-2024-05-13",
            "Provider-8/claude-3-haiku:beta": "anthropic/claude-3-haiku:beta",
            "Provider-8/claude-3-haiku": "anthropic/claude-3-haiku",
            "Provider-8/claude-3-opus:beta": "anthropic/claude-3-opus:beta",
            "Provider-8/claude-3-opus": "anthropic/claude-3-opus",
            "Provider-8/claude-3-sonnet:beta": "anthropic/claude-3-sonnet:beta",
            "Provider-8/claude-3-sonnet": "anthropic/claude-3-sonnet",
        }
        
        self.models = self._load_models()

    def _load_models(self):
        """Loads the model information for Provider 8 from the centralized Config."""
        try:
            models = []
            all_models_data = Config.ALLOWED_MODELS
            
            for model_data in all_models_data:
                if model_data.get("id", "").startswith("Provider-8/"):
                    model_config = Config.get_model_config(model_data["id"])
                    max_tokens = (model_config.get("max_input_tokens", Config.MAX_INPUT_TOKENS) + 
                                  model_config.get("max_output_tokens", Config.MAX_OUTPUT_TOKENS))
                    
                    models.append({
                        "id": model_data["id"],
                        "description": model_data.get("description", f"{model_data['id'].split('/')[-1]} model"),
                        "max_tokens": max_tokens,
                        "provider": "Provider-8",
                        "owner_cost_per_million_tokens": model_data.get("owner_cost_per_million_tokens", 0.0)
                    })
            return models
        except Exception as e:
            log.error(f"Error loading models for Provider8: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """
        Handles chat completion requests. Uses model mapping. Does not support streaming.
        """
        # Map the external model_id to the internal ID required by the API
        if model_id not in self.alias_to_actual:
            log.error(f"Model alias '{model_id}' not found in Provider 8 mapping.")
            raise ValueError(f"Unsupported model ID for Provider 8: {model_id}")
        
        internal_model_id = self.alias_to_actual[model_id]

        # Provider 8 does not support streaming, so force stream=False
        payload = {
            "model": internal_model_id, # Use the internal ID for the API call
            "messages": messages,
            "stream": False 
        }

        # Add optional parameters if provided
        for param in ["temperature", "max_tokens", "top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if param in kwargs and kwargs[param] is not None:
                payload[param] = kwargs[param]
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                stream=stream,
                timeout=180 # Add a timeout
            )

            # Raise exceptions for bad status codes immediately
            response.raise_for_status()

            # Since streaming is disabled, always process as non-streaming
            try:
                response_data = response.json()
                # Note: Token counting is deferred as per requirements
                return response_data
            except json.JSONDecodeError as e:
                log.error(f"Provider 8 JSON parsing error: {e}")
                log.error(f"Response text: {response.text[:500]}") # Log part of the raw response
                raise Exception(f"Failed to parse JSON response from Provider 8: {e}")

        except requests.exceptions.RequestException as e:
            log.error(f"Provider 8 API request failed: {e}")
            # Re-raise a more generic exception or handle specific errors
            raise Exception(f"Provider 8 API request error: {e}")
        except Exception as e:
            log.error(f"Unexpected error in Provider 8 chat_completion: {e}")
            raise # Re-raise unexpected errors

    def get_models(self) -> list:
        """Returns the list of supported models for Provider 8."""
        # Reload models in case config changed, or rely on initialized list
        # For simplicity, returning the initialized list. Consider reloading if dynamic updates are needed.
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens (input + output) for the given model."""
        for model in self.models:
            if model["id"] == model_id:
                # Use the pre-calculated max_tokens from _load_models
                return model.get("max_tokens", Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS)
        # Fallback to default if model not found in loaded list
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS

    def get_default_max_tokens(self, model_id: str) -> int:
        """Get the default maximum generation (output) tokens for the given model."""
        model_config = Config.get_model_config(model_id)
        return model_config.get("max_output_tokens", Config.MAX_OUTPUT_TOKENS)
