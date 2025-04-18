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
        # Use the API version from the environment variable, or default to the version used in the working example
        self.api_version = os.environ.get("AZURE_API_VERSION", "2024-12-01-preview")
        self.deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME") # This variable is not used in chat_completion, deployment name is extracted from model_id

        # Add logging to check environment variables
        log.info(f"Provider9 initializing with:")
        log.info(f"  AZURE_ENDPOINT: {self.azure_endpoint}")
        # Log only if API key is set, without printing the key itself
        log.info(f"  AZURE_API_KEY is set: {bool(self.api_key)}")
        log.info(f"  API Version: {self.api_version}")


        if not all([self.api_key, self.azure_endpoint]):
            log.error("Azure credentials not fully configured. Please set AZURE_API_KEY and AZURE_ENDPOINT.")
            raise ValueError("Azure credentials not fully configured.")
        log.info("Azure credentials configured.")

        # Force API version to match the working example
        forced_api_version = "2024-12-01-preview"
        log.info(f"Forcing Azure API Version to: {forced_api_version}")

        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=forced_api_version, # Use the forced API version
            )
            log.info("AzureOpenAI client initialized successfully.")
        except Exception as e:
            log.error(f"Failed to initialize AzureOpenAI client: {e}")
            raise

        self.models = self._load_models()
        log.info(f"Provider9 loaded models: {[model['id'] for model in self.models]}")


    def _load_models(self):
        """Loads the model information for this provider."""
        models_list = []
        log.info("Attempting to load models for Provider9 from config.")
        try:
            all_models_config = Config.get_models_config()
            log.info(f"Loaded all models config: {all_models_config}")
            for model_data in all_models_config:
                # Check if the model ID starts with the provider prefix
                if model_data.get("id", "").startswith("Provider-9/"):
                    log.info(f"Found Provider-9 model data: {model_data}")
                    # Use the provided max_input_tokens and max_output_tokens if available, otherwise use defaults
                    max_input = model_data.get("max_input_tokens", 32768)
                    max_output = model_data.get("max_output_tokens", 4096)
                    owner_cost = model_data.get('owner_cost_per_million_tokens', 0.00)

                    models_list.append({
                        "id": model_data["id"],
                        "description": model_data.get("description", "Azure OpenAI model"),
                        "max_tokens": max_input + max_output,
                        "provider": "Provider-9",
                        "owner_cost_per_million_tokens": owner_cost
                    })
            return models_list
        except Exception as e:
            log.error(f"Error loading models for Provider9: {e}")
            return []

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """
        Generates chat completions using Azure OpenAI.
        Handles both streaming and non-streaming requests.
        """
        supported_model_ids = [model['id'] for model in self.models]
        if model_id not in supported_model_ids:
             raise ValueError(f"Model '{model_id}' is not supported by Provider9. Supported models: {', '.join(supported_model_ids)}")


        # Extract the deployment name from the model_id
        # Assuming model_id is in the format "Provider-9/deployment-name"
        parts = model_id.split('/')
        if len(parts) != 2 or parts[0] != 'Provider-9':
             raise ValueError(f"Invalid model ID format for Provider9: {model_id}")
        deployment_name = parts[1]

        # Prepare parameters for the API call
        params = {
            "model": deployment_name, # Use the deployment name extracted from model_id
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature"),
            # Use max_completion_tokens instead of max_tokens for this Azure model
            "max_completion_tokens": kwargs.get("max_tokens", self.get_default_max_tokens(model_id)),
            "top_p": kwargs.get("top_p"),
            "presence_penalty": kwargs.get("presence_penalty"),
            "frequency_penalty": kwargs.get("frequency_penalty"),
            # Include reasoning_effort from kwargs if present, as seen in the working example
            "reasoning_effort": kwargs.get("reasoning_effort"),
        }

        # Remove None values to avoid sending them to the API
        # Also remove 'max_tokens' if it somehow made it into kwargs
        params = {k: v for k, v in params.items() if v is not None and k != 'max_tokens'}

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
        for model in self.models:
            if model["id"] == model_id:
                return model["max_tokens"]
        # Fallback if model not found
        return Config.MAX_INPUT_TOKENS + Config.MAX_OUTPUT_TOKENS # General fallback


    def get_default_max_tokens(self, model_id: str) -> int:
        """Returns the default maximum generation tokens for the given model."""
        for model in self.models:
            if model["id"] == model_id:
                 model_config = Config.get_model_config(model_id)
                 if model_config and "max_output_tokens" in model_config:
                     return model_config["max_output_tokens"]
                 else:
                     return 4000
        return Config.MAX_OUTPUT_TOKENS
