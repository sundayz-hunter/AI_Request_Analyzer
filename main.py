# -*- coding: utf-8 -*-

from burp import IBurpExtender, IMessageEditorTabFactory, ITab
from java.lang import System
import os

# Import core modules
from core.cache import AnalysisCache
from core.models import ModelManager
from core.api_handlers import OpenRouterHandler, OllamaHandler, OpenAIHandler
from utils.helpers import truncate_message

# Import UI modules
from ui.config_tab import ConfigTab
from ui.analyzer_tabs import RequestAnalyzerTab, ResponseTabFactory

class BurpExtender(IBurpExtender, IMessageEditorTabFactory, ITab):
    """
    Main extension class that registers with Burp Suite.
    """
    
    def registerExtenderCallbacks(self, callbacks):
        """
        Register the extension with Burp Suite.
        
        Args:
            callbacks: Burp's callbacks object
        """
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        stdout = callbacks.getStdout()
        stdout.write("AI Request Analyzer initializing...\n")
        
        # Load saved settings
        saved_api_key = callbacks.loadExtensionSetting("ai_analyzer_api_key") or ""
        saved_ollama_model = callbacks.loadExtensionSetting("ai_analyzer_ollama_model") or ""
        saved_openrouter_model = callbacks.loadExtensionSetting("ai_analyzer_openrouter_model") or ""
        saved_ollama_url = callbacks.loadExtensionSetting(
            "ai_analyzer_ollama_url") or "http://localhost:11434/api/generate"
        saved_use_ollama = callbacks.loadExtensionSetting("ai_analyzer_use_ollama") == "true"

        # Load OpenAI-compatible settings
        saved_openai_api_url = callbacks.loadExtensionSetting("ai_analyzer_openai_api_url") or ""
        saved_openai_api_key = callbacks.loadExtensionSetting("ai_analyzer_openai_api_key") or ""
        saved_openai_model = callbacks.loadExtensionSetting("ai_analyzer_openai_model") or ""
        saved_use_openai = callbacks.loadExtensionSetting("ai_analyzer_use_openai") == "true"
        
        # Verification and correction: ensure active model matches provider
        if saved_use_openai:
            saved_model = saved_openai_model or ""
            callbacks.saveExtensionSetting("ai_analyzer_model", saved_model)
        elif saved_use_ollama:
            saved_model = saved_ollama_model or ""
            callbacks.saveExtensionSetting("ai_analyzer_model", saved_model)
        else:
            saved_model = saved_openrouter_model or ""
            callbacks.saveExtensionSetting("ai_analyzer_model", saved_model)

        # Default configuration
        self._config = {
            "api_key": saved_api_key,
            "model": saved_model,
            "use_ollama": saved_use_ollama,
            "analyze_automatically": True,
            "ollama_url": saved_ollama_url,
            "ollama_model": saved_ollama_model,
            "openrouter_model": saved_openrouter_model,
            "openai_api_url": saved_openai_api_url,
            "openai_api_key": saved_openai_api_key,
            "openai_model": saved_openai_model,
            "use_openai": saved_use_openai,
            "suggest_prompt": self._load_prompt_file(callbacks, "prompts/suggest_prompt.txt"),
            "explain_prompt": self._load_prompt_file(callbacks, "prompts/explain_prompt.txt")
        }
        
        # Initialize model manager
        self._model_manager = ModelManager()
        
        # Initialize cache manager
        self._cache_manager = AnalysisCache(callbacks)

        # Define reference to extender in cache manager
        self._cache_manager.set_extender(self)
        
        # Set extension name
        callbacks.setExtensionName("AI Request Analyzer")
        
        # Register factories for request and response tabs
        callbacks.registerMessageEditorTabFactory(self)  # For request tabs (AI Suggest)
        callbacks.registerMessageEditorTabFactory(ResponseTabFactory(self))  # For response tabs (AI Explain)
        
        # Create config tab
        self._config_tab = ConfigTab(self)
        callbacks.addSuiteTab(self)
        
        # Initialize API handlers
        self._openrouter_handler = OpenRouterHandler(self)
        self._ollama_handler = OllamaHandler(self)
        self._openai_handler = OpenAIHandler(self)
        
        # Store callbacks for later use
        self._callbacks = callbacks

        stdout.write("AI Request Analyzer initialized successfully!\n")
    
    def getTabCaption(self):
        """
        Get the tab caption for Burp's UI.
        
        Returns:
            Tab caption string
        """
        return "AI Request Analyzer"
    
    def getUiComponent(self):
        """
        Get the UI component for the tab.
        
        Returns:
            The UI component
        """
        return self._config_tab.get_ui()
    
    def createNewInstance(self, controller, editable):
        """
        Create a new message editor tab instance.
        
        Args:
            controller: The message editor controller
            editable: Whether the tab is editable
            
        Returns:
            A new RequestAnalyzerTab instance
        """
        return RequestAnalyzerTab(self, controller, editable)
    
    def get_config(self):
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._config
    
    def set_config(self, key, value):
        """
        Update a configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        stdout = self._callbacks.getStdout()
        
        placeholder_values = [
            "",
            "Type your model name or fetch the list of available model",
            "Fetching models..."
        ]
        
        if key == "api_key":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_api_key", value)
        
        elif key == "model":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_model", value)
            
            if value not in placeholder_values:
                if self._config.get("use_ollama", False):
                    self._config["ollama_model"] = value
                    self._callbacks.saveExtensionSetting("ai_analyzer_ollama_model", value)
                else:
                    self._config["openrouter_model"] = value
                    self._callbacks.saveExtensionSetting("ai_analyzer_openrouter_model", value)
        
        elif key == "ollama_model":
            if value not in placeholder_values:
                self._config[key] = value
                self._callbacks.saveExtensionSetting("ai_analyzer_ollama_model", value)
                
                if self._config.get("use_ollama", False):
                    self._config["model"] = value
                    self._callbacks.saveExtensionSetting("ai_analyzer_model", value)
        
        elif key == "openrouter_model":
            if value not in placeholder_values:
                self._config[key] = value
                self._callbacks.saveExtensionSetting("ai_analyzer_openrouter_model", value)
                
                if not self._config.get("use_ollama", False):
                    self._config["model"] = value
                    self._callbacks.saveExtensionSetting("ai_analyzer_model", value)
        
        elif key == "ollama_url":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_ollama_url", value)
        
        elif key == "use_ollama":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_use_ollama", "true" if value else "False")

        elif key == "openai_api_url":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_openai_api_url", value)

        elif key == "openai_api_key":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_openai_api_key", value)

        elif key == "openai_model":
            if value not in placeholder_values:
                self._config[key] = value
                self._callbacks.saveExtensionSetting("ai_analyzer_openai_model", value)

                if self._config.get("use_openai", False):
                    self._config["model"] = value
                    self._callbacks.saveExtensionSetting("ai_analyzer_model", value)

        elif key == "use_openai":
            self._config[key] = value
            self._callbacks.saveExtensionSetting("ai_analyzer_use_openai", "true" if value else "False")

        else:
            self._config[key] = value
    
    # Cache management methods
    def get_cached_analysis(self, message_hash, is_request):
        """
        Get cached analysis result if available.
        
        Args:
            message_hash: Hash of the message
            is_request: Whether it's a request or response
            
        Returns:
            Cached analysis result or None
        """
        return self._cache_manager.get_cached_analysis(message_hash, is_request)
    
    def set_cached_analysis(self, message_hash, is_request, result):
        """
        Store analysis result in cache.
        
        Args:
            message_hash: Hash of the message
            is_request: Whether it's a request or response
            result: Analysis result to cache
        """
        self._cache_manager.set_cached_analysis(message_hash, is_request, result)
    
    def clear_cache(self):
        """Clear the analysis cache"""
        self._cache_manager.clear_cache()
    
    def get_cache_stats(self):
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return self._cache_manager.get_cache_stats()
    
    # Model management methods
    def get_available_models(self, use_ollama=False, use_openai=False):
        """
        Get available models.

        Args:
            use_ollama: Whether to get Ollama models
            use_openai: Whether to get OpenAI-compatible models

        Returns:
            List of model names
        """
        return self._model_manager.get_available_models(use_ollama, use_openai)

    def add_available_model(self, model, use_ollama=False, use_openai=False):
        """
        Add a model to available models.

        Args:
            model: Model name
            use_ollama: Whether it's an Ollama model
            use_openai: Whether it's an OpenAI-compatible model

        Returns:
            True if added, False if already exists
        """
        return self._model_manager.add_available_model(model, use_ollama, use_openai)

    def set_available_models(self, models, use_ollama=False, use_openai=False):
        """
        Set all available models.

        Args:
            models: List of model names
            use_ollama: Whether they're Ollama models
            use_openai: Whether they're OpenAI-compatible models
        """
        self._model_manager.set_available_models(models, use_ollama, use_openai)
    
    # API handling methods
    def get_api_handler(self, use_ollama=False, use_openai=False):
        """
        Get the appropriate API handler based on configuration.

        Args:
            use_ollama: Whether to use Ollama
            use_openai: Whether to use OpenAI-compatible

        Returns:
            API handler instance
        """
        if use_openai:
            return self._openai_handler
        if use_ollama:
            return self._ollama_handler
        else:
            return self._openrouter_handler
    
    # Message handling helpers
    def truncate_message(self, message, max_length=None):
        """
        Truncate a message to a maximum length.
        
        Args:
            message: The message to truncate
            max_length: Maximum length (if None, will be taken from config)
            
        Returns:
            Truncated message
        """
        if max_length is None:
            # Get from config
            max_length = self._config.get("MAX_MESSAGE_LENGTH", 4000)
            
        return truncate_message(message, max_length)
    
    def _load_prompt_file(self, callbacks, file_path):
        """
        Load prompt text from a file relative to the extension directory.
        
        Args:
            callbacks: Burp callbacks object
            file_path: Path to the file relative to the extension directory
            
        Returns:
            Contents of the file as a string or error message
        """
        try:
            # Get the extension directory
            extension_path = callbacks.getExtensionFilename()
            if extension_path:
                # Get the directory containing the extension
                extension_dir = os.path.dirname(extension_path)
                # Build path to the prompt file
                prompt_path = os.path.join(extension_dir, file_path)
                
                # Read and return the file contents
                with open(prompt_path, 'r') as f:
                    return f.read()
            
            # If we couldn't determine the extension path
            error_msg = "Error: Could not determine extension path to load prompt file: " + file_path
            stdout = callbacks.getStdout()
            stdout.write(error_msg + "\n")
            return error_msg
        except Exception as e:
            # If there was an error reading the file
            error_msg = "Error loading prompt file {0}: {1}".format(file_path, str(e))
            stdout = callbacks.getStdout()
            stdout.write(error_msg + "\n")
            return "Error: Prompt file not found or could not be loaded: " + file_path
    
