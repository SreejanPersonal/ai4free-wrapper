import logging
from openai import OpenAI
from .base_provider import BaseProvider
from ..config import Config
import os
from dotenv import load_dotenv; load_dotenv()

log = logging.getLogger(__name__)

class Provider3(BaseProvider):
    """
    Provider 3 implementation.
    Originally supports the models "deepseek-r1" and "o3-mini".
    Now the aliases are:
      • "Provider-3/DeepSeek-R1"  → maps to original "deepseek-r1"
      • "Provider-3/o3-mini"      → maps to original "o3-mini"
    The internal logic remains unchanged.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.environ.get("PROVIDER_3_BASE_URL"), 
            api_key=os.environ.get("PROVIDER_3_API_KEY")
        )
        self.alias_to_actual = {
            "Provider-3/DeepSeek-R1": "deepseek-r1",
            "Provider-3/o3-mini": "o3-mini"
        }
        self.models = self._load_models()

    def _load_models(self):
        """Creates the models list using the predefined alias mapping."""
        try:
            # Build two model entries using our alias-to-actual mappings.
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