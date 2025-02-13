# app/providers/base_provider.py

import abc

class BaseProvider(abc.ABC):
    """
    Abstract base class for all LLM providers.

    Defines the interface that all concrete provider implementations
    must adhere to.  This ensures consistency and allows for easy
    switching between providers.
    """

    @abc.abstractmethod
    def chat_completion(self, model_id: str, messages: list, stream: bool = False, **kwargs) -> dict:
        """
        Performs a chat completion.

        Args:
            model_id: The ID of the model to use.
            messages: A list of message dictionaries (role, content).
            stream: Whether to stream the response.
            **kwargs:  Additional provider-specific parameters.

        Returns:
            A dictionary containing the response from the LLM.  The exact
            structure will depend on the provider, but it should be consistent
            across calls to the same provider.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_models(self) -> list:
        """
        Returns a list of models supported by this provider.

        Returns:
            A list of dictionaries, where each dictionary represents a model
            and contains at least an 'id' key.

             Example:
            [
                {"id": "model_1", "description": "...", "max_tokens": 4096, "provider": "provider-1"},
                {"id": "model_2", "description": "...", "max_tokens": 8192, "provider": "provider-1"},
            ]

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_max_tokens(self, model_id: str) -> int:
        """Returns the maximum number of tokens supported by the given model."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_default_max_tokens(self, model_id: str) -> int:
      """Get the default maximum generation tokens for the given model."""
      raise NotImplementedError