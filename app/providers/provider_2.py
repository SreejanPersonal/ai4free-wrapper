from .base_provider import BaseProvider
from openai import OpenAI
import logging
import os
from dotenv import load_dotenv; load_dotenv()
from ..config import Config

log = logging.getLogger(__name__)

class Provider2(BaseProvider):
    """
    Provider implementation for Provider 2 using alias naming (Provider-2/*).
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("PROVIDER_2_BASE_URL"),
            api_key=os.getenv("PROVIDER_2_API_KEY")
        )
        self.models = self._load_models()

    def _load_models(self):
        """Loads model information and filters for Provider-2 models."""
        try:
            models_data = Config.ALLOWED_MODELS
            return [
                {
                    "id": model['id'],  # e.g., "Provider-2/gpt-4o"
                    "description": model.get('description', "No description available."),
                    "max_tokens": (
                        Config.get_model_config(model['id'])["max_input_tokens"] +
                        Config.get_model_config(model['id'])["max_output_tokens"]
                    ),
                    "provider": "Provider-2",
                    "owner_cost_per_million_tokens": model.get('owner_cost_per_million_tokens', 0.0)
                }
                for model in models_data if model['id'].startswith("Provider-2/")
            ]
        except Exception as e:
            log.error(f"Error loading models for Provider2: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs) -> dict:
        """Performs a chat completion using Provider 2 API."""
        kwargs.pop('app', None)
        try:
            completion = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=stream,
                **kwargs
            )
            if stream:
                return completion  # Return the streaming generator
            else:
                return completion.model_dump()
        except Exception as e:
            log.error(f"Provider 2 API error: {e}")
            raise

    def get_models(self) -> list:
        """Returns the list of models supported by Provider-2."""
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens for the given model alias."""
        for model in self.models:
            if model["id"] == model_id:
                return model["max_tokens"]
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS

    def get_default_max_tokens(self, model_id: str) -> int:
        """Returns the default maximum generation tokens for the given model alias."""
        for model in self.models:
            if model["id"] == model_id:
                return Config.get_model_config(model_id)["max_output_tokens"]
        return Config.MAX_OUTPUT_TOKENS