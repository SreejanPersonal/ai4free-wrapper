import requests
import json
import time
import logging
import os
from dotenv import load_dotenv; load_dotenv()
from ..utils.token_counter import count_tokens
from ..config import Config

log = logging.getLogger(__name__)

class Provider1:
    """
    Provider 1 implementation.
    This provider originally expected the model name "deepseek-ai/DeepSeek-R1".
    Now, if the alias "Provider-1/DeepSeek-R1" is provided, it is mapped
    to "deepseek-ai/DeepSeek-R1" and the original logic is retained.
    """

    def __init__(self):
        self.models = self._load_models()
        self.url = os.environ.get("PROVIDER_1_BASE_URL")
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,hi;q=0.8",
            "content-type": "text/plain;charset=UTF-8",
            "dnt": "1",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        # Mapping of alias to original model name
        self.alias_to_actual = {
            "Provider-1/DeepSeek-R1": "deepseek-ai/DeepSeek-R1"
        }

    def _load_models(self):
        """Loads the model information from the centralized file and returns the model with its alias."""
        try:
            # In the configuration file, the model metadata still uses the original name.
            # Here we simply construct a model entry that uses our alias.
            # (For Provider1, typically there is only one model.)
            return [{
                "id": "Provider-1/DeepSeek-R1",  # This is the alias now!
                "description": "Deepseek Model",
                "max_tokens": (Config.get_model_config("Provider-1/DeepSeek-R1")["max_input_tokens"] +
                               Config.get_model_config("Provider-1/DeepSeek-R1")["max_output_tokens"]),
                "provider": "Provider-1",
                "owner_cost_per_million_tokens": 2.00
            }]
        except Exception as e:
            log.error(f"Error loading models for Provider1: {e}")
            return []

    def _generate_fake_id(self):
        """Generate a dummy unique identifier for the chat completion."""
        return str(int(time.time() * 1000))

    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs):
        """
        Performs a chat completion.
        Maps the provided alias to the original model name before calling the API.
        """
        # Map alias to original model name if available; else use model_id as provided.
        actual_model = self.alias_to_actual.get(model_id, model_id)
        payload = {
            "messages": messages,
            "model": actual_model
        }
        response = requests.post(self.url, headers=self.headers, json=payload, stream=True)

        if response.status_code != 200:
            log.error(f"Provider 1 API error: Status {response.status_code}, Response: {response.text}")
            raise Exception(f"Provider 1 API error: Status {response.status_code}, Detail: {response.text}")

        if stream:
            def generate():
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith("data: "):
                        json_data = line[6:]
                        if json_data.strip() == "[DONE]":
                            continue
                        try:
                            chunk = json.loads(json_data)
                            if isinstance(chunk, dict) and "choices" in chunk and chunk["choices"]:
                                yield chunk
                        except json.JSONDecodeError as e:
                            log.error(f"JSON parsing error in stream: {e}")
                            continue
            return generate()
        else:
            full_response_content = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    json_data = line[6:] if line.startswith("data: ") else line
                    try:
                        chunk = json.loads(json_data)
                        if isinstance(chunk, dict) and "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_response_content += delta["content"]
                    except json.JSONDecodeError:
                        continue
            completion_tokens = count_tokens(
                [{"role": "assistant", "content": full_response_content}],
                model_id,
                kwargs.get('app')
            )
            prompt_tokens = count_tokens(messages, model_id, kwargs.get('app'))
            total_tokens = prompt_tokens + completion_tokens
            return {
                "id": "chatcmpl-" + self._generate_fake_id(),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_id,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": full_response_content},
                    "logprobs": None,
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "completion_tokens_details": {
                        "accepted_prediction_tokens": 0,
                        "rejected_prediction_tokens": 0,
                        "reasoning_tokens": 0
                    },
                    "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 0}
                },
                "service_tier": "default",
                "system_fingerprint": "fp_dummy"
            }

    def get_models(self) -> list:
        """Returns the supported models information for Provider 1."""
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