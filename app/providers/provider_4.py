from .base_provider import BaseProvider
import requests
import json
import os
from dotenv import load_dotenv; load_dotenv()
import logging
from ..config import Config

log = logging.getLogger(__name__)

class Provider4(BaseProvider):
    """
    Provider 4 implementation.
    This provider supports streaming responses only.
    Originally, it expected the following model names:
      • "deepseek-ai/DeepSeek-R1"
      • "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
      • "deepseek-ai/DeepSeek-V3"
    Now, the aliases are:
      • "Provider-4/DeepSeek-R1"            → maps to original "deepseek-ai/DeepSeek-R1"
      • "Provider-4/DeepSeek-R1-Distill-Llama-70B"    → maps to original "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
      • "Provider-4/DeepSeekV3"               → maps to original "deepseek-ai/DeepSeek-V3"
    The original logic for streaming is preserved.
    """

    def __init__(self):
        self.api_key = os.environ.get("PROVIDER_4_API_KEY")
        self.base_url = os.environ.get("PROVIDER_4_BASE_URL")
        self.endpoint = f"{self.base_url}/chat/completions"
        self.alias_to_actual = {
            "Provider-4/DeepSeek-R1": "deepseek-ai/DeepSeek-R1",
            "Provider-4/DeepSeek-R1-Distill-Llama-70B": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            "Provider-4/DeepSeekV3": "deepseek-ai/DeepSeek-V3"
        }

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs) -> dict:
        """
        Performs a streaming chat completion.
        Maps the alias to the actual model name.
        """
        if not stream:
            raise Exception("Provider4 does not support non-streaming requests. Enable streaming by setting stream=True.")
        if model_id not in self.alias_to_actual:
            raise Exception(f"Model '{model_id}' is not supported by Provider4.")
        actual_model = self.alias_to_actual[model_id]

        payload = {
            "model": actual_model,
            "stream": True,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 256),
            "top_p": kwargs.get("top_p", 0.1),
            "frequency_penalty": kwargs.get("frequency_penalty", 0),
            "presence_penalty": kwargs.get("presence_penalty", 0)
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, stream=True)
            if response.status_code != 200:
                log.error(f"Provider4 API error: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Provider4 API error: Status {response.status_code}, Detail: {response.text}")
            def generate():
                for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                    if not line:
                        continue
                    data_str = line[len("data:"):].strip() if line.startswith("data:") else line.strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError as e:
                        log.error(f"JSON decoding error in Provider4 stream: {e}")
                        continue
                    yield chunk
            return generate()
        except Exception as e:
            log.error(f"Error in Provider4 chat_completion: {e}")
            raise

    def get_models(self) -> list:
        """Returns the list of models for Provider4 using alias names."""
        models = []
        for alias in self.alias_to_actual.keys():
            conf = Config.get_model_config(alias)
            models.append({
                "id": alias,
                "description": f"Provider4 model ({alias})",
                "max_tokens": conf["max_input_tokens"] + conf["max_output_tokens"],
                "provider": "Provider-4",
                "owner_cost_per_million_tokens": None
            })
        return models

    def get_max_tokens(self, model_id: str) -> int:
        conf = Config.get_model_config(model_id)
        return conf["max_input_tokens"] + conf["max_output_tokens"]

    def get_default_max_tokens(self, model_id: str) -> int:
        conf = Config.get_model_config(model_id)
        return conf["max_output_tokens"]