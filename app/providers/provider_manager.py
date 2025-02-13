# app/providers/provider_manager.py

from .provider_1 import Provider1
from .provider_2 import Provider2
from .provider_3 import Provider3
from .provider_4 import Provider4
from typing import Dict, List, Optional
import logging
from . import BaseProvider

log = logging.getLogger(__name__)

class ProviderManager:
    """
    Manages available LLM providers.
    Allows for registration, provider selection based on model id, 
    and listing available models.
    """

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}

    def register_provider(self, provider_name: str, provider: BaseProvider):
        if provider_name in self.providers:
            log.warning(f"Provider '{provider_name}' already registered. Overwriting.")
        self.providers[provider_name] = provider
        log.info(f"Provider '{provider_name}' registered.")

    def register_providers(self, app):
        """Registers all available providers."""
        self.register_provider("provider-1", Provider1())
        self.register_provider("provider-2", Provider2())
        self.register_provider("provider-3", Provider3())
        self.register_provider("provider-4", Provider4())

    def select_provider(self, model_id: str) -> Optional[BaseProvider]:
        """
        Selects a provider based on the model id.
        For example, if model_id is "deepseek-r1", Provider3 will be selected.
        """
        for provider in self.providers.values():
            for model in provider.get_models():
                if model["id"] == model_id:
                    return provider
        log.warning(f"No provider found for model ID: {model_id}")
        return None

    def list_models(self) -> List[dict]:
        """Lists all available models from all providers."""
        all_models = []
        for provider in self.providers.values():
            all_models.extend(provider.get_models())
        return all_models