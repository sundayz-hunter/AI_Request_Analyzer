# -*- coding: utf-8 -*-

from java.awt.event import ActionListener, FocusListener, ItemListener, ItemEvent, KeyAdapter, KeyEvent
from javax.swing import DefaultComboBoxModel
from java.lang import Boolean, Thread, Runnable

class ConfigFieldListener(FocusListener):
    """
    Listener for configuration field updates (handles text fields and text areas).
    Updates config when field loses focus.
    """
    
    def __init__(self, extender, config_key, component):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            config_key: The configuration key to update
            component: The UI component to monitor
        """
        self._extender = extender
        self._config_key = config_key
        self._component = component
    
    def focusGained(self, event):
        # If field contains placeholder text, clear it
        if self._config_key == "api_key" and self._component.getText() == "Enter your API Key here...":
            self._component.setText("")
    
    def focusLost(self, event):
        # Update configuration when field loses focus
        new_value = self._component.getText()
        
        # For API key, handle placeholder
        if self._config_key == "api_key" and not new_value:
            self._component.setText("Enter your API Key here...")
            return
            
        # For other fields, update config with new value
        self._extender.set_config(self._config_key, new_value)


class PlaceholderFocusListener(FocusListener):
    """
    Listener for fields with placeholder text.
    Handles display and clearing of placeholder text.
    """
    
    def __init__(self, extender, config_key, component, placeholder_text):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            config_key: The configuration key to update
            component: The UI component to monitor
            placeholder_text: The placeholder text to display when empty
        """
        self._extender = extender
        self._config_key = config_key
        self._component = component
        self._placeholder_text = placeholder_text
    
    def focusGained(self, event):
        current_text = self._component.getText()
        if current_text == self._placeholder_text:
            self._component.setText("")
    
    def focusLost(self, event):
        current_text = self._component.getText()
        if not current_text:
            self._component.setText(self._placeholder_text)
        else:
            # Only update if the text is not the placeholder
            if current_text != self._placeholder_text:
                self._extender.set_config(self._config_key, current_text)


class FilterKeyListener(KeyAdapter):
    """
    Listener for filtering model dropdown based on typing.
    """
    
    def __init__(self, combo_box, all_models):
        """
        Initialize the listener.
        
        Args:
            combo_box: The combo box to filter
            all_models: List of all available models
        """
        self._combo_box = combo_box
        self._all_models = all_models
    
    def keyReleased(self, event):
        # Filter models based on text input
        filter_text = self._combo_box.getEditor().getItem().lower()
        
        # If filter text is empty or matches placeholder, show all models
        if not filter_text or filter_text == "type your model name or fetch the list of available model":
            return
            
        # Filter models that contain the filter text
        filtered_models = [model for model in self._all_models if filter_text in model.lower()]
        
        # Update the dropdown with filtered models
        self._combo_box.setModel(DefaultComboBoxModel(filtered_models))
        self._combo_box.setPopupVisible(True)
        self._combo_box.getEditor().setItem(filter_text)


class CheckboxListener(ActionListener):
    """
    Listener for checkbox state changes.
    Updates config when checkbox state changes.
    """
    
    def __init__(self, extender, config_key, checkbox):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            config_key: The configuration key to update
            checkbox: The checkbox component
        """
        self._extender = extender
        self._config_key = config_key
        self._checkbox = checkbox
    
    def actionPerformed(self, event):
        self._extender.set_config(self._config_key, self._checkbox.isSelected())


class ModelSelectionListener(ItemListener):
    """
    Listener for model selection changes.
    Updates config when model selection changes.
    """
    
    def __init__(self, extender, combo_box, use_ollama=False):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            combo_box: The combo box component
            use_ollama: Whether this is for Ollama models
        """
        self._extender = extender
        self._combo_box = combo_box
        self._use_ollama = use_ollama
    
    def itemStateChanged(self, event):
        if event.getStateChange() == ItemEvent.SELECTED:
            selected_model = self._combo_box.getSelectedItem()
            
            # Don't update if it's a placeholder or empty
            placeholder_values = [
                "",
                "Type your model name or fetch the list of available model",
                "Fetching models..."
            ]
            
            if selected_model not in placeholder_values:
                # Determine which config key to update
                if self._use_ollama:
                    self._extender.set_config("ollama_model", selected_model)
                    
                    # If we're in Ollama mode, also update the current model
                    if self._extender.get_config()["use_ollama"]:
                        self._extender.set_config("model", selected_model)
                else:
                    self._extender.set_config("openrouter_model", selected_model)
                    
                    # If we're in OpenRouter mode, also update the current model
                    if not self._extender.get_config()["use_ollama"]:
                        self._extender.set_config("model", selected_model)


class FetchModelsListener(ActionListener):
    """
    Listener for fetching models from OpenRouter.
    """
    
    def __init__(self, extender, combo_box, config_tab):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            combo_box: The combo box to update with models
            config_tab: The configuration tab for UI updates
        """
        self._extender = extender
        self._combo_box = combo_box
        self._config_tab = config_tab
    
    def actionPerformed(self, event):
        # Update UI to show fetch in progress
        editor_component = self._combo_box.getEditor().getEditorComponent()
        editor_component.setText("Fetching models...")
        
        # Disable button during fetch
        self._config_tab._fetch_models_button_openrouter.setEnabled(False)
        
        # Start fetch in a separate thread
        class FetchRunnable(Runnable):
            def __init__(self, listener):
                self._listener = listener
            
            def run(self):
                try:
                    # Get API handler from main module
                    api_handler = self._listener._extender.get_api_handler(False, False)
                    
                    # Fetch models
                    def on_complete(models, error=None):
                        if models:
                            # Update combo box
                            self._listener._extender.set_available_models(models, False)
                            self._listener._config_tab.update_model_combo(models)
                            
                            # Select the first model in the list if there are any models
                            if models and len(models) > 0:
                                self._listener._combo_box.setSelectedItem(models[0])
                                # Also update config with the selected model
                                self._listener._extender.set_config("openrouter_model", models[0])
                                self._listener._extender.set_config("model", models[0])
                            else:
                                # Reset combo box text if no models found
                                editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                                editor_component.setText("Type your model name or fetch the list of available model")
                        else:
                            # Show error
                            editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                            editor_component.setText(error or "Error fetching models. Check API key.")
                        
                        # Re-enable button
                        self._listener._config_tab._fetch_models_button_openrouter.setEnabled(True)
                    
                    # Fetch models
                    api_handler.fetch_available_models(on_complete)
                
                except Exception as e:
                    # Show error
                    editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                    editor_component.setText("Error: " + str(e))
                    
                    # Log error
                    self._listener._extender._callbacks.getStdout().write(
                        "Error fetching models from OpenRouter: " + str(e) + "\n")
                    
                    # Re-enable button
                    self._listener._config_tab._fetch_models_button_openrouter.setEnabled(True)
        
        # Start fetch thread
        fetch_thread = Thread(FetchRunnable(self))
        fetch_thread.start()


class FetchOllamaModelsListener(ActionListener):
    """
    Listener for fetching models from Ollama.
    """
    
    def __init__(self, extender, combo_box, config_tab):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
            combo_box: The combo box to update with models
            config_tab: The configuration tab for UI updates
        """
        self._extender = extender
        self._combo_box = combo_box
        self._config_tab = config_tab
    
    def actionPerformed(self, event):
        # Update UI to show fetch in progress
        editor_component = self._combo_box.getEditor().getEditorComponent()
        editor_component.setText("Fetching models...")
        
        # Disable button during fetch
        self._config_tab._fetch_models_button_ollama.setEnabled(False)
        
        # Start fetch in a separate thread
        class FetchRunnable(Runnable):
            def __init__(self, listener):
                self._listener = listener
            
            def run(self):
                try:
                    # Get API handler from main module
                    api_handler = self._listener._extender.get_api_handler(True, False)
                    
                    # Fetch models
                    def on_complete(models, error=None):
                        if models:
                            # Update combo box
                            self._listener._extender.set_available_models(models, True)
                            self._listener._config_tab.update_ollama_model_combo(models)
                            
                            # Select the first model in the list if there are any models
                            if models and len(models) > 0:
                                self._listener._combo_box.setSelectedItem(models[0])
                                # Also update config with the selected model
                                self._listener._extender.set_config("ollama_model", models[0])
                                # If in Ollama mode, also update active model
                                if self._listener._extender.get_config().get("use_ollama", False):
                                    self._listener._extender.set_config("model", models[0])
                            else:
                                # Reset combo box text if no models found
                                editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                                editor_component.setText("Type your model name or fetch the list of available model")
                        else:
                            # Show error
                            editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                            editor_component.setText(error or "Error fetching models. Check Ollama URL.")
                        
                        # Re-enable button
                        self._listener._config_tab._fetch_models_button_ollama.setEnabled(True)
                    
                    # Fetch models
                    api_handler.fetch_available_models(on_complete)
                
                except Exception as e:
                    # Show error
                    editor_component = self._listener._combo_box.getEditor().getEditorComponent()
                    editor_component.setText("Error: " + str(e))
                    
                    # Log error
                    self._listener._extender._callbacks.getStdout().write(
                        "Error fetching models from Ollama: " + str(e) + "\n")
                    
                    # Re-enable button
                    self._listener._config_tab._fetch_models_button_ollama.setEnabled(True)
        
        # Start fetch thread
        fetch_thread = Thread(FetchRunnable(self))
        fetch_thread.start()


class ApiSelectionListener(ActionListener):
    """
    Listener for API selection (OpenRouter vs Ollama vs OpenAI-compatible).
    """

    def __init__(self, extender, use_ollama=False, use_openai=False, button=None):
        """
        Initialize the listener.

        Args:
            extender: The main extender object
            use_ollama: Whether to use Ollama
            use_openai: Whether to use OpenAI-compatible
            button: Optional button reference
        """
        self._extender = extender
        self._use_ollama = use_ollama
        self._use_openai = use_openai
        self._button = button

    def actionPerformed(self, event):
        # Get the old state before changing it
        old_use_ollama = self._extender.get_config().get("use_ollama", False)
        old_use_openai = self._extender.get_config().get("use_openai", False)

        # Only make changes if the state actually changes
        if old_use_ollama != self._use_ollama or old_use_openai != self._use_openai:
            # Get reference to stdout for debugging
            stdout = self._extender._callbacks.getStdout()

            # Store current model selection before switching providers
            current_model = self._extender.get_config().get("model", "")

            # Make sure we don't store placeholder values as actual model selections
            placeholder_values = [
                "",
                "Type your model name or fetch the list of available model",
                "Fetching models..."
            ]

            # Save current model to the old provider
            if old_use_openai and current_model and current_model not in placeholder_values:
                self._extender.set_config("openai_model", current_model)
            elif old_use_ollama and current_model and current_model not in placeholder_values:
                self._extender.set_config("ollama_model", current_model)
            elif not old_use_ollama and not old_use_openai and current_model and current_model not in placeholder_values:
                self._extender.set_config("openrouter_model", current_model)

            # Load model for the new provider
            if self._use_openai:
                openai_model = self._extender.get_config().get("openai_model", "")
                if openai_model and openai_model not in placeholder_values:
                    self._extender._config["model"] = openai_model
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", openai_model)
                else:
                    self._extender._config["model"] = ""
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", "")
            elif self._use_ollama:
                ollama_model = self._extender.get_config().get("ollama_model", "")
                if ollama_model and ollama_model not in placeholder_values:
                    self._extender._config["model"] = ollama_model
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", ollama_model)
                else:
                    self._extender._config["model"] = ""
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", "")
            else:
                openrouter_model = self._extender.get_config().get("openrouter_model", "")
                if openrouter_model and openrouter_model not in placeholder_values:
                    self._extender._config["model"] = openrouter_model
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", openrouter_model)
                else:
                    self._extender._config["model"] = ""
                    self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", "")

            # Update provider flags AFTER handling model switching
            self._extender.set_config("use_ollama", self._use_ollama)
            self._extender.set_config("use_openai", self._use_openai)

            # Make sure the model-specific settings are correctly synchronized
            if self._use_openai:
                openai_model = self._extender.get_config().get("openai_model", "")
                self._extender._callbacks.saveExtensionSetting("ai_analyzer_openai_model", openai_model)
            elif self._use_ollama:
                ollama_model = self._extender.get_config().get("ollama_model", "")
                self._extender._callbacks.saveExtensionSetting("ai_analyzer_ollama_model", ollama_model)
            else:
                openrouter_model = self._extender.get_config().get("openrouter_model", "")
                self._extender._callbacks.saveExtensionSetting("ai_analyzer_openrouter_model", openrouter_model)

            # Update configuration panels
            try:
                # Get the ConfigTab
                config_tab = self._extender._config_tab
                # Update the interface
                if config_tab:
                    config_tab.update_config_panels()

                    # Update button text if button is provided
                    if self._button:
                        self._button.setText("Hive" if self._use_ollama else "View")
            except Exception as e:
                stdout.write("Error updating UI after API selection: " + str(e) + "\n")


class TogglePasswordVisibilityListener(ActionListener):
    """
    Listener for toggling API key visibility.
    """
    
    def __init__(self, config_tab):
        """
        Initialize the listener.
        
        Args:
            config_tab: The configuration tab
        """
        self._config_tab = config_tab
    
    def actionPerformed(self, event):
        # Toggle between "View" and "Hide"
        current_button_text = self._config_tab._toggle_api_key_button.getText()
        actual_key = self._config_tab._extender.get_config()["api_key"]
        
        # Toggle state
        self._config_tab._is_api_key_hidden = not self._config_tab._is_api_key_hidden
        
        # Update UI based on new state
        if self._config_tab._is_api_key_hidden:
            # If hiding, change to "View" and mask the key
            self._config_tab._toggle_api_key_button.setText("View")
            if actual_key and actual_key != "Enter your API Key here...":
                self._config_tab._api_key_field.setText('*' * len(actual_key))
        else:
            # If showing, change to "Hide" and show the key
            self._config_tab._toggle_api_key_button.setText("Hide")
            if actual_key and actual_key != "Enter your API Key here...":
                self._config_tab._api_key_field.setText(actual_key)


class ToggleOllamaUrlVisibilityListener(ActionListener):
    """
    Listener for toggling Ollama URL visibility.
    """
    
    def __init__(self, config_tab):
        """
        Initialize the listener.
        
        Args:
            config_tab: The configuration tab
        """
        self._config_tab = config_tab
    
    def actionPerformed(self, event):
        # Toggle visibility state
        self._config_tab._is_ollama_url_hidden = not self._config_tab._is_ollama_url_hidden
        
        # Get the actual URL from config
        actual_url = self._config_tab._extender.get_config()["ollama_url"]
        
        # If no URL, do nothing
        if not actual_url:
            return
        
        # Update display based on state
        if self._config_tab._is_ollama_url_hidden:
            # Mask the URL
            self._config_tab._ollama_url_field.setText('*' * len(actual_url))
            # Update button text
            self._config_tab._toggle_ollama_url_button.setText("View")
        else:
            # Show the URL
            self._config_tab._ollama_url_field.setText(actual_url)
            # Update button text
            self._config_tab._toggle_ollama_url_button.setText("Hide")
        
        # Force UI update
        self._config_tab._ollama_url_field.revalidate()
        self._config_tab._ollama_url_field.repaint()
        self._config_tab._toggle_ollama_url_button.revalidate()
        self._config_tab._toggle_ollama_url_button.repaint()

class ClearCacheListener(ActionListener):
    """
    Listener for clearing the analysis cache.
    """
    
    def __init__(self, extender):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
        self._config_tab = None  # To be set later
    
    def actionPerformed(self, event):
        # Clear the cache
        self._extender.clear_cache()
        
        # Log cache clearing
        stdout = self._extender._callbacks.getStdout()
        stdout.write("Analysis cache cleared!\n")
        
        # Update cache statistics in UI
        if self._config_tab:
            self._config_tab.update_cache_stats()


class ClearSettingsListener(ActionListener):
    """
    Listener for resetting all settings.
    """
    
    def __init__(self, extender):
        """
        Initialize the listener.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
    
    def actionPerformed(self, event):
        # Preserve current provider selection
        current_use_ollama = self._extender._config.get("use_ollama", False)
        current_use_openai = self._extender._config.get("use_openai", False)

        # Reset all settings
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_api_key", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_model", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_ollama_model", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_openrouter_model", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_ollama_url",
                                                       "http://localhost:11434/api/generate")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_openai_api_url", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_openai_api_key", "")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_openai_model", "")

        # Keep the provider selection
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_use_ollama",
                                                      "true" if current_use_ollama else "False")
        self._extender._callbacks.saveExtensionSetting("ai_analyzer_use_openai",
                                                      "true" if current_use_openai else "False")

        # Reset the config
        self._extender._config = {
            "api_key": "",
            "model": "",
            "use_ollama": current_use_ollama,
            "use_openai": current_use_openai,
            "analyze_automatically": True,
            "ollama_url": "http://localhost:11434/api/generate",
            "ollama_model": "",
            "openrouter_model": "",
            "openai_api_url": "",
            "openai_api_key": "",
            "openai_model": "",
            "suggest_prompt": self._extender._config.get("suggest_prompt", ""),
            "explain_prompt": self._extender._config.get("explain_prompt", "")
        }
        
        # Update UI text fields
        try:
            # Get config tab reference
            config_tab = self._extender._config_tab
            
            # Reset API key field and visibility state
            if hasattr(config_tab, "_api_key_field") and config_tab._api_key_field:
                config_tab._api_key_field.setText("Enter your API Key here...")
                # The API key field switches to visible mode after reset
                config_tab._is_api_key_hidden = False
                
                # Force button text to "Hide" (visible mode)
                if hasattr(config_tab, "_toggle_api_key_button"):
                    config_tab._toggle_api_key_button.setText("Hide")
            
            # Reset model combos
            placeholder_text = "Type your model name or fetch the list of available model"
            if hasattr(config_tab, "_model_combo") and config_tab._model_combo:
                editor = config_tab._model_combo.getEditor()
                editor_component = editor.getEditorComponent()
                if editor_component:
                    editor_component.setText(placeholder_text)
            
            if hasattr(config_tab, "_ollama_model_combo") and config_tab._ollama_model_combo:
                editor = config_tab._ollama_model_combo.getEditor()
                editor_component = editor.getEditorComponent()
                if editor_component:
                    editor_component.setText(placeholder_text)
            
            # Reset Ollama URL field and visibility state
            if hasattr(config_tab, "_ollama_url_field") and config_tab._ollama_url_field:
                config_tab._ollama_url_field.setText("http://localhost:11434/api/generate")
                # For Ollama URL, switch to visible mode after reset
                config_tab._is_ollama_url_hidden = False

                # Force button text to "Hide" (visible mode)
                if hasattr(config_tab, "_toggle_ollama_url_button"):
                    config_tab._toggle_ollama_url_button.setText("Hide")

            # Reset OpenAI-compatible fields
            if hasattr(config_tab, "_openai_url_field") and config_tab._openai_url_field:
                config_tab._openai_url_field.setText("https://api.openai.com/v1/chat/completions")
                config_tab._is_openai_url_hidden = False
                if hasattr(config_tab, "_toggle_openai_url_button"):
                    config_tab._toggle_openai_url_button.setText("View")

            if hasattr(config_tab, "_openai_api_key_field") and config_tab._openai_api_key_field:
                config_tab._openai_api_key_field.setText("Enter your API Key here...")
                config_tab._is_openai_api_key_hidden = False
                if hasattr(config_tab, "_toggle_openai_api_key_button"):
                    config_tab._toggle_openai_api_key_button.setText("View")

            if hasattr(config_tab, "_openai_model_field") and config_tab._openai_model_field:
                config_tab._openai_model_field.setText("Enter your model name (e.g., gpt-4)")
            
            # Update UI
            config_tab.update_config_panels()
            
            # Log reset
            self._extender._callbacks.getStdout().write("User settings have been reset!\n")
        except Exception as e:
            try:
                self._extender._callbacks.getStdout().write("Error updating UI after settings reset: " + str(e) + "\n")
            except:
                pass


class ReloadAnalysisListener(ActionListener):
    """
    Listener for the "Reload Analysis" button in analyzer tabs.
    """
    
    def __init__(self, tab):
        """
        Initialize the listener.
        
        Args:
            tab: The analyzer tab containing this button
        """
        self._tab = tab
    
    def actionPerformed(self, event):
        # Trigger analysis
        self._tab.analyze()


class ToggleOpenAIUrlVisibilityListener(ActionListener):
    """
    Listener for toggling OpenAI URL visibility.
    """

    def __init__(self, config_tab):
        """
        Initialize the listener.

        Args:
            config_tab: The configuration tab
        """
        self._config_tab = config_tab

    def actionPerformed(self, event):
        # Toggle visibility state
        self._config_tab._is_openai_url_hidden = not self._config_tab._is_openai_url_hidden

        # Get the actual URL from config
        actual_url = self._config_tab._extender.get_config().get("openai_api_url", "")
        placeholder = "https://api.openai.com/v1/chat/completions"

        # If no URL or placeholder, do nothing
        if not actual_url or actual_url == placeholder:
            return

        # Update display based on state
        if self._config_tab._is_openai_url_hidden:
            # Mask the URL
            self._config_tab._openai_url_field.setText('*' * len(actual_url))
            # Update button text
            self._config_tab._toggle_openai_url_button.setText("View")
        else:
            # Show the URL
            self._config_tab._openai_url_field.setText(actual_url)
            # Update button text
            self._config_tab._toggle_openai_url_button.setText("Hide")

        # Force UI update
        self._config_tab._openai_url_field.revalidate()
        self._config_tab._openai_url_field.repaint()
        self._config_tab._toggle_openai_url_button.revalidate()
        self._config_tab._toggle_openai_url_button.repaint()


class ToggleOpenAIKeyVisibilityListener(ActionListener):
    """
    Listener for toggling OpenAI API key visibility.
    """

    def __init__(self, config_tab):
        """
        Initialize the listener.

        Args:
            config_tab: The configuration tab
        """
        self._config_tab = config_tab

    def actionPerformed(self, event):
        # Toggle state
        current_button_text = self._config_tab._toggle_openai_api_key_button.getText()
        actual_key = self._config_tab._extender.get_config().get("openai_api_key", "")
        placeholder = "Enter your API Key here..."

        # Toggle state
        self._config_tab._is_openai_api_key_hidden = not self._config_tab._is_openai_api_key_hidden

        # Update UI based on new state
        if self._config_tab._is_openai_api_key_hidden:
            # If hiding, change to "View" and mask the key
            self._config_tab._toggle_openai_api_key_button.setText("View")
            if actual_key and actual_key != placeholder:
                self._config_tab._openai_api_key_field.setText('*' * len(actual_key))
        else:
            # If showing, change to "Hide" and show the key
            self._config_tab._toggle_openai_api_key_button.setText("Hide")
            if actual_key and actual_key != placeholder:
                self._config_tab._openai_api_key_field.setText(actual_key)
