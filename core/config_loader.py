# -*- coding: utf-8 -*-

import os
import re

class ConfigLoader:
    """
    Loads configuration from .env file with fallback to default values.
    """
    
    def __init__(self, callbacks):
        """
        Initialize the config loader.
        
        Args:
            callbacks: Burp's callbacks object
        """
        self._callbacks = callbacks
        self._stdout = callbacks.getStdout()
        self._config = {}
        self._env_path = None
        
        # Default configuration values
        self._defaults = {
            # Cache settings
            "CACHE_MAX_SIZE_MB": 100,
            "CACHE_MAX_AGE_DAYS": 30,
            "CACHE_MAX_ENTRIES": 1000,
            
            # Message settings
            "MAX_MESSAGE_LENGTH": 4000,
            
            # OpenRouter settings
            "OPENROUTER_MAX_TOKENS": 800,
            "OPENROUTER_API_URL": "https://openrouter.ai/api/v1/chat/completions",
            "OPENROUTER_DEFAULT_MODEL": "",
            "OPENROUTER_TEMPERATURE": 0.3,
            
            # Ollama settings
            "OLLAMA_API_URL": "http://localhost:11434/api/generate",
            "OLLAMA_DEFAULT_MODEL": "",
            "OLLAMA_TEMPERATURE": 0.3
        }
        
        # Try to load .env file
        try:
            extension_path = callbacks.getExtensionFilename()
            if extension_path:
                # Get the directory containing the extension
                extension_dir = os.path.dirname(extension_path)
                # Path to .env file
                self._env_path = os.path.join(extension_dir, ".env")
                
                # Load config if .env exists
                if os.path.exists(self._env_path):
                    self._load_env_file()
                else:
                    self._config = self._defaults.copy()
            else:
                self._config = self._defaults.copy()
        except Exception as e:
            self._stdout.write("Error loading config: " + str(e) + "\n")
            self._config = self._defaults.copy()
    
    def _load_env_file(self):
        """Load configuration from .env file"""
        try:
            with open(self._env_path, 'r') as f:
                env_content = f.read()
            
            # Parse .env file
            self._config = self._defaults.copy()  # Start with defaults
            
            # Simple regex to parse key-value pairs, ignoring comments
            pattern = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*(.+)$', re.MULTILINE)
            matches = pattern.findall(env_content)
            
            for key, value in matches:
                # Skip commented lines
                if key.strip().startswith('#'):
                    continue
                
                # Convert value to appropriate type
                try:
                    # Try to convert to numeric value if possible
                    if value.isdigit():
                        self._config[key] = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        self._config[key] = float(value)
                    else:
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        self._config[key] = value
                except Exception:
                    # Use the string value if conversion fails
                    self._config[key] = value

        except Exception as e:
            self._stdout.write("Error parsing .env file: " + str(e) + "\n")
            self._config = self._defaults.copy()
    
    def get(self, key, default=None):
        """
        Get configuration value for a key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)