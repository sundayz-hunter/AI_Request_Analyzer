# -*- coding: utf-8 -*-

class ModelManager:
    """
    Manages AI model selection and availability for OpenRouter, Ollama, and OpenAI-compatible providers.
    """

    def __init__(self):
        """Initialize the model manager with empty model lists"""
        self._available_models = []  # OpenRouter models
        self._available_ollama_models = []  # Ollama models
        self._available_openai_models = []  # OpenAI-compatible models

    def get_available_models(self, use_ollama=False, use_openai=False):
        """
        Get the list of available models.

        Args:
            use_ollama: Whether to get Ollama models
            use_openai: Whether to get OpenAI-compatible models

        Returns:
            List of available model names
        """
        if use_openai:
            return self._available_openai_models
        return self._available_ollama_models if use_ollama else self._available_models

    def add_available_model(self, model, use_ollama=False, use_openai=False):
        """
        Add a model to the available models list.

        Args:
            model: Model name to add
            use_ollama: Whether to add to Ollama models
            use_openai: Whether to add to OpenAI-compatible models

        Returns:
            True if model was added, False if it was already in the list
        """
        if use_openai:
            model_list = self._available_openai_models
        elif use_ollama:
            model_list = self._available_ollama_models
        else:
            model_list = self._available_models

        if model not in model_list:
            model_list.append(model)
            return True
        return False

    def set_available_models(self, models, use_ollama=False, use_openai=False):
        """
        Set the complete list of available models.

        Args:
            models: List of model names
            use_ollama: Whether to set Ollama models
            use_openai: Whether to set OpenAI-compatible models
        """
        # Always sort models alphabetically
        if models:
            models.sort()

        if use_openai:
            self._available_openai_models = models
        elif use_ollama:
            self._available_ollama_models = models
        else:
            self._available_models = models
