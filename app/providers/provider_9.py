import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError
from .base_provider import BaseProvider
from ..config import Config

log = logging.getLogger(__name__)
load_dotenv()

class Provider9(BaseProvider):
    """
    Provider for Azure OpenAI Service.
    Supports gpt-4.1 model.
    """

    def __init__(self):
        self.api_key = os.environ.get("AZURE_API_KEY")
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_version = os.environ.get("AZURE_API_VERSION", "2024-02-01") # Default API version if not set
        self.deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME") # The deployment name for the model

        if not all([self.api_key, self.azure_endpoint, self.deployment_name]):
            log.error("Azure credentials not fully configured. Please set AZURE_API_KEY, AZURE_ENDPOINT, and AZURE_DEPLOYMENT_NAME.")
            raise ValueError("Azure credentials not fully configured.")

        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version,
            )
        except Exception as e:
            log.error(f"Failed to initialize AzureOpenAI client: {e}")
            raise

        self.model_id = "Provider-9/gpt-4.1"
        self.models = self._load_models()


    def _load_models(self):
        """Loads the model information for this provider."""
        try:
            model_config = Config.get_model_config(self.model_id)
            max_input = model_config.get("max_input_tokens")
            max_output = model_config.get("max_output_tokens",)
            owner_cost = model_config.get('owner_cost_per_million_tokens', 2.00) # Default cost if not specified

            return [{
                "id": self.model_id,
                "description": "Azure OpenAI gpt-4.1 model",
                "max_tokens": max_input + max_output,
                "provider": "Provider-9",
                "owner_cost_per_million_tokens": owner_cost
            }]
        except Exception as e:
            log.error(f"Error loading models for Provider9: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """
        Generates chat completions using Azure OpenAI.
        Handles both streaming and non-streaming requests.
        """
        if model_id != self.model_id:
            raise ValueError(f"Model '{model_id}' is not supported by Provider9. Only {self.model_id} is supported.")

        # Prepare parameters for the API call
        params = {
            "model": self.deployment_name, # Use the deployment name specified in .env
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature"),
            "max_tokens": kwargs.get("max_tokens", self.get_default_max_tokens(model_id)),
            "top_p": kwargs.get("top_p"),
            "presence_penalty": kwargs.get("presence_penalty"),
            "frequency_penalty": kwargs.get("frequency_penalty"),
        }

        # Remove None values to avoid sending them to the API
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.client.chat.completions.create(**params)

            if stream:
                return response
            else:
                return response.model_dump()

        except (APITimeoutError, RateLimitError, APIError) as e:
            log.error(f"Azure API error: {type(e).__name__} - {e}")
            # Re-raise a more generic exception or handle specific errors
            raise Exception(f"Azure API Error: {e}") from e
        except Exception as e:
            log.error(f"Unexpected error in Provider9 chat_completion: {e}")
            raise

    def get_models(self) -> list:
        """Returns the list of supported models for Provider9."""
        return self.models

    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens (input + output) for the given model."""
        if model_id == self.model_id and self.models:
            return self.models[0]["max_tokens"]
        # Fallback if model list is empty or ID doesn't match
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS # General fallback

    def get_default_max_tokens(self, model_id: str) -> int:
        """Returns the default maximum generation tokens for the given model."""
        if model_id == self.model_id:
             model_config = Config.get_model_config(self.model_id)
             if model_config and "max_output_tokens" in model_config:
                 return model_config["max_output_tokens"]
             else:
                 return 4096
        return Config.MAX_OUTPUT_TOKENS
