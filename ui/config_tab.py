# -*- coding: utf-8 -*-

from javax.swing import JPanel, JTabbedPane, JTextField, JLabel, JButton, JComboBox, JScrollPane
from javax.swing import JTextArea, JCheckBox, Box, BoxLayout, BorderFactory, UIManager, ImageIcon
from javax.swing import ButtonGroup, JRadioButton, JSeparator, DefaultComboBoxModel
from java.awt import BorderLayout, Font, GridLayout, Dimension, Color, Component, CardLayout
from java.awt import GridBagLayout, GridBagConstraints, Insets
from java.lang import Float, Boolean

from utils.listeners import ApiSelectionListener, CheckboxListener, ConfigFieldListener
from utils.listeners import FilterKeyListener, ModelSelectionListener, PlaceholderFocusListener
from utils.listeners import ClearCacheListener, ClearSettingsListener
from utils.listeners import FetchModelsListener, FetchOllamaModelsListener
from utils.listeners import TogglePasswordVisibilityListener, ToggleOllamaUrlVisibilityListener
from utils.listeners import ToggleOpenAIUrlVisibilityListener, ToggleOpenAIKeyVisibilityListener

# Shared constants for placeholders and dimensions
MODEL_PLACEHOLDER = "Type your model name or fetch the list of available model"
API_KEY_PLACEHOLDER = "Enter your API Key here..."
OPENAI_URL_PLACEHOLDER = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL_PLACEHOLDER = "Enter your model name (e.g., gpt-4)"
OLLAMA_URL_DEFAULT = "http://localhost:11434/api/generate"

FIELD_DIM = Dimension(530, 25)
ROW_DIM = Dimension(600, 30)
EYE_BUTTON_DIM = Dimension(40, 25)


class ConfigTab:
    """
    Configuration tab for the extension.
    Provides UI for configuring API keys, models, and settings.
    """
    
    def __init__(self, extender):
        """
        Initialize the configuration tab.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
        
        # UI state tracking
        self._is_api_key_hidden = True
        self._is_ollama_url_hidden = True
        self._is_openai_url_hidden = True
        self._is_openai_api_key_hidden = True
        
        # Create main panel
        self._panel = JPanel(BorderLayout(20, 20))
        self._panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20))
        
        # Set panel dimensions
        self._panel.setMinimumSize(Dimension(1000, 600))
        self._panel.setPreferredSize(Dimension(1000, 600))
        self._panel.setMaximumSize(Dimension(1200, 800))
        
        # Use Burp Suite colors
        burp_background = UIManager.getColor("Panel.background")
        if burp_background:
            self._panel.setBackground(burp_background)
        
        # Create form panel
        form_panel = JPanel(BorderLayout())
        form_panel.setBorder(BorderFactory.createEmptyBorder(0, 0, 10, 0))
        if burp_background:
            form_panel.setBackground(burp_background)
        
        # Central panel with BoxLayout
        central_panel = JPanel()
        central_panel.setLayout(BoxLayout(central_panel, BoxLayout.Y_AXIS))
        central_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            central_panel.setBackground(burp_background)
        
        # Center the central panel
        form_panel.add(central_panel, BorderLayout.CENTER)
        
        # ====== MAIN CONFIG LAYOUT ======
        # Main container panel
        centering_panel = JPanel()
        centering_panel.setLayout(BorderLayout())
        if burp_background:
            centering_panel.setBackground(burp_background)
        
        # Inner panel for side-by-side panels
        inner_panel = JPanel()
        inner_panel.setLayout(BorderLayout(10, 0))
        if burp_background:
            inner_panel.setBackground(burp_background)
        
        # Fixed configuration for centering with larger API field
        inner_panel.setPreferredSize(Dimension(950, 230))
        inner_panel.setMaximumSize(Dimension(950, 230))
        inner_panel.setMinimumSize(Dimension(950, 230))
        inner_panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10))
        
        # Create panels for each section with balanced proportions
        left_panel = JPanel()
        left_panel.setLayout(BoxLayout(left_panel, BoxLayout.Y_AXIS))
        left_panel.setPreferredSize(Dimension(700, 210))
        left_panel.setMinimumSize(Dimension(700, 210))
        left_panel.setMaximumSize(Dimension(700, 210))
        left_panel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5))
        if burp_background:
            left_panel.setBackground(burp_background)
        
        right_panel = JPanel()
        right_panel.setLayout(BoxLayout(right_panel, BoxLayout.Y_AXIS))
        right_panel.setPreferredSize(Dimension(250, 210))
        right_panel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5))
        if burp_background:
            right_panel.setBackground(burp_background)
        
        # API Configuration title - centered
        api_header_panel = JPanel()
        api_header_panel.setLayout(BoxLayout(api_header_panel, BoxLayout.Y_AXIS))
        api_header_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        api_header_panel.setMaximumSize(Dimension(700, 50))
        if burp_background:
            api_header_panel.setBackground(burp_background)
        
        api_header_label = JLabel("API Configuration")
        api_header_label.setFont(Font("Dialog", Font.BOLD, 16))
        api_header_label.setAlignmentX(Component.CENTER_ALIGNMENT)
        api_header_panel.add(api_header_label)
        api_header_panel.add(Box.createVerticalStrut(10))
        
        # Horizontal separator
        api_separator = JSeparator()
        api_separator.setMaximumSize(Dimension(700, 2))
        api_separator.setAlignmentX(Component.CENTER_ALIGNMENT)
        api_header_panel.add(api_separator)
        api_header_panel.add(Box.createVerticalStrut(15))
        
        left_panel.add(api_header_panel)
        
        # Create radio buttons for API selection - centered
        radio_panel = JPanel(BorderLayout())
        radio_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            radio_panel.setBackground(burp_background)
        
        # Center panel for radio buttons with spacing
        radio_center_panel = JPanel()
        radio_center_panel.setLayout(GridLayout(1, 3, 20, 0))
        radio_center_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        radio_center_panel.setMaximumSize(Dimension(700, 30))
        radio_center_panel.setPreferredSize(Dimension(700, 30))
        if burp_background:
            radio_center_panel.setBackground(burp_background)
        
        # Create button group
        api_button_group = ButtonGroup()
        
        # Create OpenRouter radio
        self._openrouter_radio = JRadioButton("OpenRouter", not self._extender.get_config()["use_ollama"] and not self._extender.get_config().get("use_openai", False))
        self._openrouter_radio.setHorizontalAlignment(JRadioButton.CENTER)
        self._openrouter_radio.setPreferredSize(Dimension(120, 25))
        self._openrouter_radio.setMaximumSize(Dimension(120, 25))
        self._openrouter_radio.setMinimumSize(Dimension(120, 25))
        self._openrouter_radio.addActionListener(ApiSelectionListener(self._extender, False, False))
        api_button_group.add(self._openrouter_radio)

        # Create Ollama radio
        self._ollama_radio = JRadioButton("Ollama", self._extender.get_config()["use_ollama"])
        self._ollama_radio.setHorizontalAlignment(JRadioButton.CENTER)
        self._ollama_radio.setPreferredSize(Dimension(100, 25))
        self._ollama_radio.setMaximumSize(Dimension(100, 25))
        self._ollama_radio.setMinimumSize(Dimension(100, 25))
        self._ollama_radio.addActionListener(ApiSelectionListener(self._extender, True, False))
        api_button_group.add(self._ollama_radio)

        # Create OpenAI-compatible radio
        self._openai_radio = JRadioButton("OpenAI-compatible", self._extender.get_config().get("use_openai", False))
        self._openai_radio.setHorizontalAlignment(JRadioButton.CENTER)
        self._openai_radio.setPreferredSize(Dimension(140, 25))
        self._openai_radio.setMaximumSize(Dimension(140, 25))
        self._openai_radio.setMinimumSize(Dimension(140, 25))
        self._openai_radio.addActionListener(ApiSelectionListener(self._extender, False, True))
        api_button_group.add(self._openai_radio)

        # Add radios to panel
        radio_center_panel.add(self._openrouter_radio)
        radio_center_panel.add(self._ollama_radio)
        radio_center_panel.add(self._openai_radio)
        
        # Add a glue on both sides to center the radio buttons
        radio_panel.add(radio_center_panel, BorderLayout.CENTER)
        
        # Add to left panel, centered
        radio_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        radio_panel.setMaximumSize(Dimension(500, 30))
        left_panel.add(Box.createVerticalStrut(10))
        left_panel.add(radio_panel)
        left_panel.add(Box.createVerticalStrut(20))
        
        # Add API configuration panels (OpenRouter/Ollama) with CardLayout
        self._config_panels = JPanel(CardLayout())
        if burp_background:
            self._config_panels.setBackground(burp_background)
        
        # OpenRouter config panel
        openrouter_config_panel = JPanel()
        openrouter_config_panel.setLayout(BoxLayout(openrouter_config_panel, BoxLayout.Y_AXIS))
        openrouter_config_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            openrouter_config_panel.setBackground(burp_background)
        
        # API Key field with placeholder instead of label
        api_key_panel = JPanel()
        api_key_panel.setLayout(BoxLayout(api_key_panel, BoxLayout.X_AXIS))
        api_key_panel.setMaximumSize(Dimension(600, 30))
        api_key_panel.setPreferredSize(Dimension(600, 30))
        api_key_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            api_key_panel.setBackground(burp_background)
        api_key_panel.add(Box.createHorizontalGlue())
        
        # Add space on the left equivalent to the button for perfect centering
        api_key_panel.add(Box.createHorizontalStrut(32))
        
        # API Key container panel WITHOUT eye button - just the field
        api_key_container_panel = JPanel()
        api_key_container_panel.setLayout(BoxLayout(api_key_container_panel, BoxLayout.X_AXIS))
        api_key_container_panel.setMaximumSize(Dimension(530, 25))  # Same size as model+fetch
        api_key_container_panel.setPreferredSize(Dimension(530, 25))
        if burp_background:
            api_key_container_panel.setBackground(burp_background)
        
        # Use a standard JTextField to avoid issues with JPasswordField
        self._api_key_field = JTextField("", 100)
        self._api_key_field.setText(self._extender.get_config()["api_key"] or "Enter your API Key here...")
        self._api_key_field.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(Color.GRAY),
            BorderFactory.createEmptyBorder(2, 5, 2, 5)
        ))
        self._api_key_field.setPreferredSize(Dimension(530, 25))  # Same size as model+fetch
        self._api_key_field.setMaximumSize(Dimension(530, 25))
        self._api_key_field.setMinimumSize(Dimension(530, 25))
        self._api_key_field.addFocusListener(
            PlaceholderFocusListener(self._extender, "api_key", self._api_key_field, "Enter your API Key here..."))
        
        # Add the text field first
        api_key_container_panel.add(self._api_key_field)
        
        # Add the centered container
        api_key_panel.add(api_key_container_panel)
        
        # Add the button outside the centered container
        # Eye button for toggling password visibility
        self._toggle_api_key_button = JButton("View")  # Initialize with "View"
        self._toggle_api_key_button.putClientProperty("hideActionText", Boolean.TRUE)
        self._toggle_api_key_button.setBorderPainted(False)  # Remove border
        self._toggle_api_key_button.setContentAreaFilled(False)  # Remove background
        self._toggle_api_key_button.setFocusPainted(False)
        self._toggle_api_key_button.setForeground(Color.GRAY)  # Gray text
        self._toggle_api_key_button.setPreferredSize(Dimension(40, 25))
        self._toggle_api_key_button.setMaximumSize(Dimension(40, 25))
        self._toggle_api_key_button.setMinimumSize(Dimension(40, 25))
        self._toggle_api_key_button.setMargin(Insets(0, 0, 0, 0))  # Zero margin to reduce space
        self._toggle_api_key_button.setToolTipText("Toggle API key visibility")
        self._toggle_api_key_button.addActionListener(TogglePasswordVisibilityListener(self))
        
        # Initially mask the API key if it's not the placeholder
        if self._api_key_field.getText() != "Enter your API Key here...":
            actual_key = self._api_key_field.getText()
            masked_key = '*' * len(actual_key)
            self._api_key_field.setText(masked_key)
            self._toggle_api_key_button.setText("View")  # Explicitly force initial text
        
        # Add a small space between the field and button
        api_key_panel.add(Box.createHorizontalStrut(2))
        
        # Add the button outside the centered container
        api_key_panel.add(self._toggle_api_key_button)
        
        api_key_panel.add(Box.createHorizontalGlue())
        api_key_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        openrouter_config_panel.add(api_key_panel)
        openrouter_config_panel.add(Box.createVerticalStrut(10))
        
        # Model selection with the same width as the API field
        model_selection_panel = JPanel()
        model_selection_panel.setLayout(BoxLayout(model_selection_panel, BoxLayout.X_AXIS))
        model_selection_panel.setMaximumSize(Dimension(600, 30))
        model_selection_panel.setPreferredSize(Dimension(600, 30))
        model_selection_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            model_selection_panel.setBackground(burp_background)
        
        model_selection_panel.add(Box.createHorizontalGlue())
        
        # Container to align ComboBox + button with a fixed width exactly equal to the API field
        model_controls_panel = JPanel()
        model_controls_panel.setLayout(BoxLayout(model_controls_panel, BoxLayout.X_AXIS))
        model_controls_panel.setMaximumSize(Dimension(530, 25))  # Adjusted to match exactly
        model_controls_panel.setPreferredSize(Dimension(530, 25))
        if burp_background:
            model_controls_panel.setBackground(burp_background)
        
        # ComboBox with placeholder - occupies available space
        self._model_combo = JComboBox(self._extender.get_available_models())
        self._model_combo.setEditable(True)
        # Standardize placeholder text for OpenRouter
        editor = self._model_combo.getEditor()
        editor_component = editor.getEditorComponent()
        if isinstance(editor_component, JTextField):
            if not self._extender.get_config()["model"]:
                editor_component.setText("Type your model name or fetch the list of available model")
            editor_component.addKeyListener(FilterKeyListener(self._model_combo, self._extender.get_available_models()))
            editor_component.addFocusListener(PlaceholderFocusListener(self._extender, "model", editor_component,
                                                                      "Type your model name or fetch the list of available model"))
        
        # Ensure selection is correct for current mode (OpenRouter)
        current_mode = self._extender.get_config().get("use_ollama", False)
        current_model = ""
        
        if not current_mode:  # OpenRouter
            current_model = self._extender.get_config().get("openrouter_model", "")
            if current_model:
                self._model_combo.setSelectedItem(current_model)
            else:
                self._model_combo.setSelectedItem("Type your model name or fetch the list of available model")
        else:
            # Even in Ollama mode, initialize correctly
            self._model_combo.setSelectedItem("Type your model name or fetch the list of available model")
        
        self._model_combo.addItemListener(ModelSelectionListener(self._extender, self._model_combo))
        
        # Adjust ComboBox width so with button they match exactly the API key field size
        self._model_combo.setPreferredSize(Dimension(400, 25))  # Adjusted so combo + button = 530px
        self._model_combo.setMaximumSize(Dimension(400, 25))
        self._model_combo.setMinimumSize(Dimension(400, 25))
        
        # Both Fetch Models buttons should have the same fixed size
        self._fetch_models_button_openrouter = JButton("Fetch Models")
        self._fetch_models_button_openrouter.setPreferredSize(Dimension(120, 25))
        self._fetch_models_button_openrouter.setMinimumSize(Dimension(120, 25))
        self._fetch_models_button_openrouter.setMaximumSize(Dimension(120, 25))
        self._fetch_models_button_openrouter.addActionListener(FetchModelsListener(self._extender, self._model_combo, self))
        self._fetch_models_button_openrouter.setToolTipText(
            "After fetching, you can type keywords like 'claude', 'gpt' or 'free' to filter models")
        
        # Add ComboBox + button to the controls panel
        model_controls_panel.add(self._model_combo)
        model_controls_panel.add(Box.createHorizontalStrut(10))  # 10px spacing
        model_controls_panel.add(self._fetch_models_button_openrouter)
        
        # Add the control panel to the main panel
        model_selection_panel.add(model_controls_panel)
        
        # Add space between controls and View/Hide button
        model_selection_panel.add(Box.createHorizontalStrut(5))
        
        # Add View/Hide button next to controls (not inside)
        # Create a grayed-out view button without border - invisible
        view_button_openrouter = JButton("View")
        view_button_openrouter.setForeground(Color.GRAY)
        view_button_openrouter.setBorderPainted(False)  # Remove border
        view_button_openrouter.setContentAreaFilled(False)  # Remove fill
        view_button_openrouter.setFocusPainted(False)
        view_button_openrouter.setPreferredSize(Dimension(40, 25))
        view_button_openrouter.setMaximumSize(Dimension(40, 25))
        view_button_openrouter.setMinimumSize(Dimension(40, 25))
        view_button_openrouter.setVisible(False)  # Make button invisible
        model_selection_panel.add(view_button_openrouter)
        
        model_selection_panel.add(Box.createHorizontalGlue())
        
        # Add panel to container
        model_selection_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        model_selection_panel.setMaximumSize(Dimension(600, 30))
        model_selection_panel.setPreferredSize(Dimension(600, 30))
        openrouter_config_panel.add(model_selection_panel)
        
        self._config_panels.add(openrouter_config_panel, "OpenRouter")
        
        # Ollama config panel
        ollama_config_panel = JPanel()
        ollama_config_panel.setLayout(BoxLayout(ollama_config_panel, BoxLayout.Y_AXIS))
        ollama_config_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            ollama_config_panel.setBackground(burp_background)
        
        # URL field - identical style to OpenRouter
        ollama_url_panel = JPanel()
        ollama_url_panel.setLayout(BoxLayout(ollama_url_panel, BoxLayout.X_AXIS))
        ollama_url_panel.setMaximumSize(Dimension(600, 30))
        ollama_url_panel.setPreferredSize(Dimension(600, 30))
        ollama_url_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            ollama_url_panel.setBackground(burp_background)
        
        ollama_url_panel.add(Box.createHorizontalGlue())
        
        # Add space on the left equivalent to the button for perfect centering
        ollama_url_panel.add(Box.createHorizontalStrut(32))
        
        # Container for URL - just the field (no button)
        ollama_url_container = JPanel()
        ollama_url_container.setLayout(BoxLayout(ollama_url_container, BoxLayout.X_AXIS))
        ollama_url_container.setMaximumSize(Dimension(530, 25))  # Same size as model+fetch
        ollama_url_container.setPreferredSize(Dimension(530, 25))
        if burp_background:
            ollama_url_container.setBackground(burp_background)
        
        # URL field with border
        self._ollama_url_field = JTextField(self._extender.get_config()["ollama_url"], 60)
        self._ollama_url_field.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(Color.GRAY),
            BorderFactory.createEmptyBorder(2, 5, 2, 5)
        ))
        self._ollama_url_field.setPreferredSize(Dimension(530, 25))  # Same size as model+fetch
        self._ollama_url_field.setMaximumSize(Dimension(530, 25))
        self._ollama_url_field.setMinimumSize(Dimension(530, 25))
        self._ollama_url_field.addFocusListener(ConfigFieldListener(self._extender, "ollama_url", self._ollama_url_field))
        
        # Add only the text field to the container
        ollama_url_container.add(self._ollama_url_field)
        
        # Add the centered container
        ollama_url_panel.add(ollama_url_container)
        
        # Add a small space between the field and button
        ollama_url_panel.add(Box.createHorizontalStrut(2))
        
        # Add the button outside the centered container
        # Eye button for toggling URL visibility
        self._toggle_ollama_url_button = JButton("View")
        self._toggle_ollama_url_button.putClientProperty("hideActionText", Boolean.TRUE)
        self._toggle_ollama_url_button.setBorderPainted(False)  # Remove border
        self._toggle_ollama_url_button.setContentAreaFilled(False)  # Remove background
        self._toggle_ollama_url_button.setFocusPainted(False)
        self._toggle_ollama_url_button.setForeground(Color.GRAY)  # Gray text
        self._toggle_ollama_url_button.setPreferredSize(Dimension(40, 25))
        self._toggle_ollama_url_button.setMaximumSize(Dimension(40, 25))
        self._toggle_ollama_url_button.setMinimumSize(Dimension(40, 25))
        self._toggle_ollama_url_button.setMargin(Insets(0, 0, 0, 0))  # Zero margin to reduce space
        self._toggle_ollama_url_button.setToolTipText("Toggle URL visibility")
        self._toggle_ollama_url_button.addActionListener(ToggleOllamaUrlVisibilityListener(self))
        
        # Initially mask the Ollama URL
        if self._ollama_url_field.getText() != "":
            actual_url = self._ollama_url_field.getText()
            masked_url = '*' * len(actual_url)
            self._ollama_url_field.setText(masked_url)
        
        # Add the button outside the centered container
        ollama_url_panel.add(self._toggle_ollama_url_button)
        
        ollama_url_panel.add(Box.createHorizontalGlue())
        
        ollama_url_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        ollama_config_panel.add(ollama_url_panel)
        ollama_config_panel.add(Box.createVerticalStrut(10))
        
        # Model selection - same style as OpenRouter
        ollama_model_panel = JPanel()
        ollama_model_panel.setLayout(BoxLayout(ollama_model_panel, BoxLayout.X_AXIS))
        ollama_model_panel.setMaximumSize(Dimension(600, 30))
        ollama_model_panel.setPreferredSize(Dimension(600, 30))
        ollama_model_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            ollama_model_panel.setBackground(burp_background)
        
        ollama_model_panel.add(Box.createHorizontalGlue())
        
        # Main control container with exact same size as URL field
        ollama_model_controls_panel = JPanel()
        ollama_model_controls_panel.setLayout(BoxLayout(ollama_model_controls_panel, BoxLayout.X_AXIS))
        ollama_model_controls_panel.setMaximumSize(Dimension(530, 25))  # Adjusted to match exactly
        ollama_model_controls_panel.setPreferredSize(Dimension(530, 25))
        if burp_background:
            ollama_model_controls_panel.setBackground(burp_background)
        
        # ComboBox - same style as OpenRouter
        self._ollama_model_combo = JComboBox(self._extender.get_available_models(True))
        self._ollama_model_combo.setEditable(True)
        # Adjust ComboBox width so with button they match exactly the URL field size
        self._ollama_model_combo.setPreferredSize(Dimension(400, 25))  # Adjusted so combo + button = 530px
        self._ollama_model_combo.setMaximumSize(Dimension(400, 25))
        self._ollama_model_combo.setMinimumSize(Dimension(400, 25))
        
        ollama_editor = self._ollama_model_combo.getEditor()
        ollama_editor_component = ollama_editor.getEditorComponent()
        if isinstance(ollama_editor_component, JTextField):
            ollama_editor_component.addKeyListener(
                FilterKeyListener(self._ollama_model_combo, self._extender.get_available_models(True)))
            
            # Add standardized placeholder for Ollama
            ollama_current_model = self._extender.get_config().get("ollama_model", "")
            if not ollama_current_model:
                ollama_editor_component.setText("Type your model name or fetch the list of available model")
            
            ollama_editor_component.addFocusListener(
                ConfigFieldListener(self._extender, "ollama_model", ollama_editor_component))
        
        # Initialize model selection for Ollama
        current_mode = self._extender.get_config().get("use_ollama", False)
        ollama_model = self._extender.get_config().get("ollama_model", "")
        
        if current_mode and ollama_model:  # If in Ollama mode and a model is defined
            self._ollama_model_combo.setSelectedItem(ollama_model)
        else:
            self._ollama_model_combo.setSelectedItem("Type your model name or fetch the list of available model")
        
        self._ollama_model_combo.addItemListener(ModelSelectionListener(self._extender, self._ollama_model_combo, True))
        
        # Fetch Models button - identical dimensions to OpenRouter
        self._fetch_models_button_ollama = JButton("Fetch Models")
        self._fetch_models_button_ollama.setPreferredSize(Dimension(120, 25))
        self._fetch_models_button_ollama.setMinimumSize(Dimension(120, 25))
        self._fetch_models_button_ollama.setMaximumSize(Dimension(120, 25))
        self._fetch_models_button_ollama.addActionListener(
            FetchOllamaModelsListener(self._extender, self._ollama_model_combo, self))
        self._fetch_models_button_ollama.setToolTipText(
            "After fetching, you can type keywords like 'llama' or 'wizard' to filter models")
        
        # Add with correct spacing
        ollama_model_controls_panel.add(self._ollama_model_combo)
        ollama_model_controls_panel.add(Box.createHorizontalStrut(10))  # 10px spacing
        ollama_model_controls_panel.add(self._fetch_models_button_ollama)
        
        ollama_model_panel.add(ollama_model_controls_panel)
        
        # Add space between controls and View/Hide button
        ollama_model_panel.add(Box.createHorizontalStrut(5))
        
        # Add View/Hide button next to controls (not inside)
        # Create a grayed-out view button without border - invisible
        view_button_ollama = JButton("View")
        view_button_ollama.setForeground(Color.GRAY)
        view_button_ollama.setBorderPainted(False)  # Remove border
        view_button_ollama.setContentAreaFilled(False)  # Remove fill
        view_button_ollama.setFocusPainted(False)
        view_button_ollama.setPreferredSize(Dimension(40, 25))
        view_button_ollama.setMaximumSize(Dimension(40, 25))
        view_button_ollama.setMinimumSize(Dimension(40, 25))
        view_button_ollama.setVisible(False)  # Make button invisible
        ollama_model_panel.add(view_button_ollama)
        
        ollama_model_panel.add(Box.createHorizontalGlue())
        
        ollama_model_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        ollama_config_panel.add(ollama_model_panel)
        
        self._config_panels.add(ollama_config_panel, "Ollama")

        # OpenAI-compatible config panel
        openai_config_panel = JPanel()
        openai_config_panel.setLayout(BoxLayout(openai_config_panel, BoxLayout.Y_AXIS))
        openai_config_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            openai_config_panel.setBackground(burp_background)

        # URL field - identical style to OpenRouter and Ollama
        openai_url_panel = JPanel()
        openai_url_panel.setLayout(BoxLayout(openai_url_panel, BoxLayout.X_AXIS))
        openai_url_panel.setMaximumSize(Dimension(600, 30))
        openai_url_panel.setPreferredSize(Dimension(600, 30))
        openai_url_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            openai_url_panel.setBackground(burp_background)

        openai_url_panel.add(Box.createHorizontalGlue())

        # Add space on the left equivalent to the button for perfect centering
        openai_url_panel.add(Box.createHorizontalStrut(32))

        # Container for URL - just the field (no button)
        openai_url_container = JPanel()
        openai_url_container.setLayout(BoxLayout(openai_url_container, BoxLayout.X_AXIS))
        openai_url_container.setMaximumSize(Dimension(530, 25))  # Same size as model+fetch
        openai_url_container.setPreferredSize(Dimension(530, 25))
        if burp_background:
            openai_url_container.setBackground(burp_background)

        # URL field with border
        saved_openai_url = self._extender.get_config().get("openai_api_url", "")
        openai_url_placeholder = "Enter OpenAI API URL here..."
        self._openai_url_field = JTextField(saved_openai_url or openai_url_placeholder, 60)
        self._openai_url_field.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(Color.GRAY),
            BorderFactory.createEmptyBorder(2, 5, 2, 5)
        ))
        self._openai_url_field.setPreferredSize(Dimension(530, 25))  # Same size as model+fetch
        self._openai_url_field.setMaximumSize(Dimension(530, 25))
        self._openai_url_field.setMinimumSize(Dimension(530, 25))
        self._openai_url_field.addFocusListener(
            PlaceholderFocusListener(self._extender, "openai_api_url", self._openai_url_field, openai_url_placeholder))

        # Add only the text field to the container
        openai_url_container.add(self._openai_url_field)

        # Add the centered container
        openai_url_panel.add(openai_url_container)

        # Add a small space between the field and button
        openai_url_panel.add(Box.createHorizontalStrut(2))

        # Add the button outside the centered container
        # Eye button for toggling URL visibility
        self._toggle_openai_url_button = JButton("View")
        self._toggle_openai_url_button.putClientProperty("hideActionText", Boolean.TRUE)
        self._toggle_openai_url_button.setBorderPainted(False)  # Remove border
        self._toggle_openai_url_button.setContentAreaFilled(False)  # Remove background
        self._toggle_openai_url_button.setFocusPainted(False)
        self._toggle_openai_url_button.setForeground(Color.GRAY)  # Gray text
        self._toggle_openai_url_button.setPreferredSize(Dimension(40, 25))
        self._toggle_openai_url_button.setMaximumSize(Dimension(40, 25))
        self._toggle_openai_url_button.setMinimumSize(Dimension(40, 25))
        self._toggle_openai_url_button.setMargin(Insets(0, 0, 0, 0))  # Zero margin to reduce space
        self._toggle_openai_url_button.setToolTipText("Toggle URL visibility")
        self._toggle_openai_url_button.addActionListener(ToggleOpenAIUrlVisibilityListener(self))

        # Initially mask the OpenAI URL if it's not empty and not a placeholder
        if saved_openai_url:
            masked_url = '*' * len(saved_openai_url)
            self._openai_url_field.setText(masked_url)

        # Add the button outside the centered container
        openai_url_panel.add(self._toggle_openai_url_button)

        openai_url_panel.add(Box.createHorizontalGlue())

        openai_url_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        openai_config_panel.add(openai_url_panel)
        openai_config_panel.add(Box.createVerticalStrut(10))

        # API Key field with placeholder - identical style to OpenRouter
        openai_api_key_panel = JPanel()
        openai_api_key_panel.setLayout(BoxLayout(openai_api_key_panel, BoxLayout.X_AXIS))
        openai_api_key_panel.setMaximumSize(Dimension(600, 30))
        openai_api_key_panel.setPreferredSize(Dimension(600, 30))
        openai_api_key_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            openai_api_key_panel.setBackground(burp_background)
        openai_api_key_panel.add(Box.createHorizontalGlue())

        # Add space on the left equivalent to the button for perfect centering
        openai_api_key_panel.add(Box.createHorizontalStrut(32))

        # API Key container panel WITHOUT eye button - just the field
        openai_api_key_container_panel = JPanel()
        openai_api_key_container_panel.setLayout(BoxLayout(openai_api_key_container_panel, BoxLayout.X_AXIS))
        openai_api_key_container_panel.setMaximumSize(Dimension(530, 25))  # Same size as model field
        openai_api_key_container_panel.setPreferredSize(Dimension(530, 25))
        if burp_background:
            openai_api_key_container_panel.setBackground(burp_background)

        # API Key field
        saved_openai_key = self._extender.get_config().get("openai_api_key", "")
        openai_key_placeholder = "Enter your API Key here..."
        self._openai_api_key_field = JTextField(saved_openai_key or openai_key_placeholder, 100)
        self._openai_api_key_field.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(Color.GRAY),
            BorderFactory.createEmptyBorder(2, 5, 2, 5)
        ))
        self._openai_api_key_field.setPreferredSize(Dimension(530, 25))  # Same size as model field
        self._openai_api_key_field.setMaximumSize(Dimension(530, 25))
        self._openai_api_key_field.setMinimumSize(Dimension(530, 25))

        # Add focus listener for saving config with placeholder
        self._openai_api_key_field.addFocusListener(
            PlaceholderFocusListener(self._extender, "openai_api_key", self._openai_api_key_field, openai_key_placeholder))

        # Add the text field first
        openai_api_key_container_panel.add(self._openai_api_key_field)

        # Add the centered container
        openai_api_key_panel.add(openai_api_key_container_panel)

        # Add a small space between the field and button
        openai_api_key_panel.add(Box.createHorizontalStrut(2))

        # Add the button outside the centered container
        # Eye button for toggling API key visibility
        self._toggle_openai_api_key_button = JButton("View")
        self._toggle_openai_api_key_button.putClientProperty("hideActionText", Boolean.TRUE)
        self._toggle_openai_api_key_button.setBorderPainted(False)  # Remove border
        self._toggle_openai_api_key_button.setContentAreaFilled(False)  # Remove background
        self._toggle_openai_api_key_button.setFocusPainted(False)
        self._toggle_openai_api_key_button.setForeground(Color.GRAY)  # Gray text
        self._toggle_openai_api_key_button.setPreferredSize(Dimension(40, 25))
        self._toggle_openai_api_key_button.setMaximumSize(Dimension(40, 25))
        self._toggle_openai_api_key_button.setMinimumSize(Dimension(40, 25))
        self._toggle_openai_api_key_button.setMargin(Insets(0, 0, 0, 0))  # Zero margin to reduce space
        self._toggle_openai_api_key_button.setToolTipText("Toggle API key visibility")
        self._toggle_openai_api_key_button.addActionListener(ToggleOpenAIKeyVisibilityListener(self))

        # Initially mask the API key if it's not empty
        if saved_openai_key:
            masked_key = '*' * len(saved_openai_key)
            self._openai_api_key_field.setText(masked_key)
            self._toggle_openai_api_key_button.setText("View")  # Explicitly force initial text

        # Add the button outside the centered container
        openai_api_key_panel.add(self._toggle_openai_api_key_button)

        openai_api_key_panel.add(Box.createHorizontalGlue())
        openai_api_key_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        openai_config_panel.add(openai_api_key_panel)
        openai_config_panel.add(Box.createVerticalStrut(10))

        # Model name field - no fetch button
        openai_model_panel = JPanel()
        openai_model_panel.setLayout(BoxLayout(openai_model_panel, BoxLayout.X_AXIS))
        openai_model_panel.setMaximumSize(Dimension(600, 30))
        openai_model_panel.setPreferredSize(Dimension(600, 30))
        openai_model_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        if burp_background:
            openai_model_panel.setBackground(burp_background)

        openai_model_panel.add(Box.createHorizontalGlue())

        # Container for model field with exact same size as URL field
        openai_model_container = JPanel()
        openai_model_container.setLayout(BoxLayout(openai_model_container, BoxLayout.X_AXIS))
        openai_model_container.setMaximumSize(Dimension(530, 25))  # Same size as URL field
        openai_model_container.setPreferredSize(Dimension(530, 25))
        if burp_background:
            openai_model_container.setBackground(burp_background)

        # Model name text field
        saved_openai_model = self._extender.get_config().get("openai_model", "")
        openai_model_placeholder = "Enter your model name (e.g., gpt-4)"
        self._openai_model_field = JTextField(saved_openai_model or openai_model_placeholder, 60)
        self._openai_model_field.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(Color.GRAY),
            BorderFactory.createEmptyBorder(2, 5, 2, 5)
        ))
        self._openai_model_field.setPreferredSize(Dimension(530, 25))  # Same size as URL field
        self._openai_model_field.setMaximumSize(Dimension(530, 25))
        self._openai_model_field.setMinimumSize(Dimension(530, 25))
        self._openai_model_field.addFocusListener(
            PlaceholderFocusListener(self._extender, "openai_model", self._openai_model_field, openai_model_placeholder))

        # Add the model field to the container
        openai_model_container.add(self._openai_model_field)

        # Add the container to the panel
        openai_model_panel.add(openai_model_container)

        # Add a placeholder view button (invisible) for alignment
        view_button_openai = JButton("View")
        view_button_openai.setForeground(Color.GRAY)
        view_button_openai.setBorderPainted(False)  # Remove border
        view_button_openai.setContentAreaFilled(False)  # Remove fill
        view_button_openai.setFocusPainted(False)
        view_button_openai.setPreferredSize(Dimension(40, 25))
        view_button_openai.setMaximumSize(Dimension(40, 25))
        view_button_openai.setMinimumSize(Dimension(40, 25))
        view_button_openai.setVisible(False)  # Make button invisible
        openai_model_panel.add(Box.createHorizontalStrut(2))
        openai_model_panel.add(view_button_openai)

        openai_model_panel.add(Box.createHorizontalGlue())

        openai_model_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        openai_config_panel.add(openai_model_panel)

        self._config_panels.add(openai_config_panel, "OpenAI")
        
        self._config_panels.setAlignmentX(Component.CENTER_ALIGNMENT)
        left_panel.add(self._config_panels)
        
        # ====== RIGHT PANEL - OPTIONS ======
        right_panel = JPanel()
        right_panel.setLayout(BoxLayout(right_panel, BoxLayout.Y_AXIS))
        # Définir des tailles du panneau droit avec des largeurs minimales augmentées
        right_panel.setPreferredSize(Dimension(250, 210))
        right_panel.setMinimumSize(Dimension(250, 210))     # Largeur minimale augmentée
        right_panel.setMaximumSize(Dimension(250, 210))
        # Modify right panel with additional left padding to compensate for separator alignment
        right_panel.setBorder(BorderFactory.createEmptyBorder(5, 15, 5, 5))  # Extra left padding
        if burp_background:
            right_panel.setBackground(burp_background)
        
        # Options title centered
        options_header_panel = JPanel()
        options_header_panel.setLayout(BoxLayout(options_header_panel, BoxLayout.Y_AXIS))
        options_header_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        options_header_panel.setMaximumSize(Dimension(250, 50))  # Augmenté pour correspondre à la largeur du panneau
        if burp_background:
            options_header_panel.setBackground(burp_background)
        
        options_header_label = JLabel("Options")
        options_header_label.setFont(Font("Dialog", Font.BOLD, 16))
        options_header_label.setAlignmentX(Component.CENTER_ALIGNMENT)
        options_header_panel.add(options_header_label)
        options_header_panel.add(Box.createVerticalStrut(10))
        
        # Horizontal separator with proper sizing
        options_separator = JSeparator()
        options_separator.setMaximumSize(Dimension(250, 2))  # Augmenté pour correspondre à la largeur du panneau
        options_separator.setAlignmentX(Component.CENTER_ALIGNMENT)
        options_header_panel.add(options_separator)
        options_header_panel.add(Box.createVerticalStrut(15))
        
        right_panel.add(options_header_panel)
        
        # Auto-analyze option - Centered
        auto_analyze_panel = JPanel()
        auto_analyze_panel.setLayout(BoxLayout(auto_analyze_panel, BoxLayout.X_AXIS))
        if burp_background:
            auto_analyze_panel.setBackground(burp_background)
        
        auto_analyze_panel.add(Box.createHorizontalGlue())
        auto_label = JLabel("Auto Analyzer:", JLabel.LEFT)
        auto_label.setPreferredSize(Dimension(120, 20))  # Taille minimale pour éviter la troncature
        auto_label.setMinimumSize(Dimension(120, 20))    # Taille minimale pour éviter la troncature
        auto_analyze_panel.add(auto_label)
        auto_analyze_panel.add(Box.createHorizontalStrut(10))
        self._auto_analyze_checkbox = JCheckBox("", self._extender.get_config()["analyze_automatically"])
        self._auto_analyze_checkbox.addActionListener(
            CheckboxListener(self._extender, "analyze_automatically", self._auto_analyze_checkbox))
        auto_analyze_panel.add(self._auto_analyze_checkbox)
        auto_analyze_panel.add(Box.createHorizontalGlue())
        
        auto_analyze_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        auto_analyze_panel.setMaximumSize(Dimension(250, 30))  # Augmenté pour correspondre à la largeur du panneau
        right_panel.add(auto_analyze_panel)
        right_panel.add(Box.createVerticalStrut(10))
        
        # Clear cache option with button on right
        clear_cache_panel = JPanel()
        clear_cache_panel.setLayout(BoxLayout(clear_cache_panel, BoxLayout.X_AXIS))
        if burp_background:
            clear_cache_panel.setBackground(burp_background)
        
        # Add cache information
        cache_stats = self._extender.get_cache_stats()
        self._cache_size_label = JLabel("Cache (" + cache_stats["size_str"] + "):", JLabel.LEFT)
        self._cache_size_label.setPreferredSize(Dimension(120, 20))  # Taille minimale pour éviter la troncature
        self._cache_size_label.setMinimumSize(Dimension(120, 20))    # Taille minimale pour éviter la troncature
        
        clear_cache_panel.add(self._cache_size_label)
        clear_cache_panel.add(Box.createHorizontalGlue())  # Add flexible space to push button to right
        self._clear_cache_button = JButton("Clear")
        clear_cache_listener = ClearCacheListener(self._extender)
        clear_cache_listener._config_tab = self
        self._clear_cache_button.addActionListener(clear_cache_listener)
        clear_cache_panel.add(self._clear_cache_button)
        
        clear_cache_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        clear_cache_panel.setMaximumSize(Dimension(250, 30))  # Augmenté pour correspondre à la largeur du panneau
        right_panel.add(clear_cache_panel)
        right_panel.add(Box.createVerticalStrut(10))
        
        # Settings reset option - button on right
        settings_panel = JPanel()
        settings_panel.setLayout(BoxLayout(settings_panel, BoxLayout.X_AXIS))
        if burp_background:
            settings_panel.setBackground(burp_background)
        
        settings_label = JLabel("Settings:", JLabel.LEFT)
        settings_label.setPreferredSize(Dimension(120, 20))  # Taille minimale pour éviter la troncature
        settings_label.setMinimumSize(Dimension(120, 20))    # Taille minimale pour éviter la troncature
        settings_panel.add(settings_label)
        settings_panel.add(Box.createHorizontalGlue())  # Add flexible space to push button to right
        self._clear_settings_button = JButton("Reset")
        self._clear_settings_button.addActionListener(ClearSettingsListener(self._extender))
        settings_panel.add(self._clear_settings_button)
        
        settings_panel.setAlignmentX(Component.CENTER_ALIGNMENT)
        settings_panel.setMaximumSize(Dimension(250, 30))  # Augmenté pour correspondre à la largeur du panneau
        right_panel.add(settings_panel)
        
        # Improve vertical alignment and standardize style of both panels
        left_panel.setPreferredSize(Dimension(700, 210))
        left_panel.setMinimumSize(Dimension(700, 210))
        left_panel.setMaximumSize(Dimension(700, 210))
        left_panel.setBorder(BorderFactory.createEmptyBorder(10, 5, 10, 5))
        
        # Standardize right panel style with left panel
        right_panel.setPreferredSize(Dimension(250, 210))
        right_panel.setMinimumSize(Dimension(250, 210))
        right_panel.setMaximumSize(Dimension(250, 210))
        right_panel.setBorder(BorderFactory.createEmptyBorder(10, 15, 10, 5))
        
        # GridBagLayout wrapper panel for perfect horizontal and vertical centering
        centering_panel = JPanel(GridBagLayout())
        if burp_background:
            centering_panel.setBackground(burp_background)
        
        # Configure container to use 2-panel layout approach with perfect centering
        config_container_panel = JPanel(BorderLayout(10, 0))
        config_container_panel.setPreferredSize(Dimension(950, 230))
        config_container_panel.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0))
        if burp_background:
            config_container_panel.setBackground(burp_background)
        
        # Add both panels side by side
        config_container_panel.add(left_panel, BorderLayout.CENTER)
        config_container_panel.add(right_panel, BorderLayout.EAST)
        
        # Set the wrapper panel background
        centering_panel.setBackground(burp_background)
        
        # Center the configuration panel in the centeringPanel with GridBagLayout
        gbc = GridBagConstraints()
        gbc.gridx = 0
        gbc.gridy = 0
        gbc.anchor = GridBagConstraints.CENTER  # Force perfect centering
        centering_panel.add(config_container_panel, gbc)
        
        # Add the centering panel to the central panel
        central_panel.add(centering_panel)
        
        # Show the right config panel based on selection
        self.update_config_panels()
        
        # Center the centralPanel in the form with precise layout
        form_panel.add(central_panel, BorderLayout.CENTER)
        form_panel.setBorder(BorderFactory.createEmptyBorder(0, 20, 10, 20))  # Add horizontal margins
        
        # Add form panel to the main panel
        self._panel.add(form_panel, BorderLayout.NORTH)
        
        # ====== PROMPT SETUP SECTION ======
        # Create a panel for prompt configuration with proper centering
        prompts_panel = JPanel(BorderLayout(10, 10))
        prompts_panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10))
        
        if burp_background:
            prompts_panel.setBackground(burp_background)
        
        # Wrapper to center tabs perfectly
        prompts_wrapper = JPanel(BorderLayout())
        prompts_wrapper.setMaximumSize(Dimension(800, 300))
        prompts_wrapper.setPreferredSize(Dimension(800, 300))
        if burp_background:
            prompts_wrapper.setBackground(burp_background)
        
        # Get Burp's tab appearance settings
        burp_tab_font = UIManager.getFont("TabbedPane.font")
        if not burp_tab_font:
            burp_tab_font = Font("Dialog", Font.PLAIN, 12)  # Fallback
        
        # Create tabbed pane for the prompt types using Burp's native style
        prompt_tabs = JTabbedPane()
        
        # Apply Burp's native tab styling with bold font and larger size
        bold_font = Font("Dialog", Font.BOLD, 14)  # Increased size for better visibility
        UIManager.put("TabbedPane.font", bold_font)
        UIManager.put("TabbedPane.selected", burp_background)
        UIManager.put("TabbedPane.background", UIManager.getColor("TabbedPane.background"))
        UIManager.put("TabbedPane.foreground", UIManager.getColor("TabbedPane.foreground"))
        
        # AI Suggest Prompt
        suggest_panel = JPanel(BorderLayout(5, 5))
        if burp_background:
            suggest_panel.setBackground(burp_background)
        
        # Get font settings directly from Burp UI with moderate increase
        burp_font = UIManager.getFont("TextArea.font")
        if not burp_font:
            # Fallback only if Burp font not available
            burp_font = Font("Consolas", Font.PLAIN, 14)
        
        # Slightly increase font size (10% larger)
        font_size = burp_font.getSize()
        larger_font = burp_font.deriveFont(Float(font_size * 1.1))
        
        suggest_prompt = JTextArea(10, 40)
        suggest_prompt.setEditable(True)
        suggest_prompt.setFont(larger_font)
        suggest_prompt.setText(self._extender.get_config().get("suggest_prompt", ""))
        
        # Add listener to save the prompt when modified
        suggest_prompt.addFocusListener(ConfigFieldListener(self._extender, "suggest_prompt", suggest_prompt))
        
        suggest_panel.add(JScrollPane(suggest_prompt), BorderLayout.CENTER)
        # Add tabs with strong bold styling
        prompt_tabs.addTab("AI Suggest Prompt", suggest_panel)
        prompt_tabs.setFont(bold_font)
        
        # Force bold font for tab titles without color
        for i in range(prompt_tabs.getTabCount()):
            prompt_tabs.setTitleAt(i, "<html><b>" + prompt_tabs.getTitleAt(i) + "</b></html>")
        
        # AI Explain Prompt
        explain_panel = JPanel(BorderLayout(5, 5))
        if burp_background:
            explain_panel.setBackground(burp_background)
        
        explain_prompt = JTextArea(10, 40)
        explain_prompt.setEditable(True)
        explain_prompt.setFont(larger_font)  # Using the same larger font
        explain_prompt.setText(self._extender.get_config().get("explain_prompt", ""))
        
        # Add listener to save the prompt when modified
        explain_prompt.addFocusListener(ConfigFieldListener(self._extender, "explain_prompt", explain_prompt))
        
        explain_panel.add(JScrollPane(explain_prompt), BorderLayout.CENTER)
        prompt_tabs.addTab("AI Explain Prompt", explain_panel)
        
        # Apply bold font to all tab titles without color
        for i in range(prompt_tabs.getTabCount()):
            prompt_tabs.setTitleAt(i, "<html><b>" + prompt_tabs.getTitleAt(i) + "</b></html>")
        
        # Add tabs to the prompts wrapper panel with perfect alignment
        prompts_wrapper.add(prompt_tabs, BorderLayout.CENTER)
        
        # Add wrapper to main prompts panel with perfect centering
        center_panel = JPanel(BorderLayout())
        if burp_background:
            center_panel.setBackground(burp_background)
        center_panel.add(Box.createHorizontalStrut(20), BorderLayout.WEST)  # Add margin
        center_panel.add(prompts_wrapper, BorderLayout.CENTER)
        center_panel.add(Box.createHorizontalStrut(20), BorderLayout.EAST)  # Add margin
        prompts_panel.add(center_panel, BorderLayout.CENTER)
        
        # Add prompts panel directly to main panel
        self._panel.add(prompts_panel, BorderLayout.CENTER)
    
    def get_ui(self):
        """
        Get the UI component for the tab.
        
        Returns:
            The JPanel containing the tab UI
        """
        return self._panel
    
    def update_config_panels(self):
        """
        Update the config panels based on the current API selection.
        """
        try:
            stdout = self._extender._callbacks.getStdout()
            layout = self._config_panels.getLayout()

            if isinstance(layout, CardLayout):
                use_ollama = self._extender.get_config().get("use_ollama", False)
                use_openai = self._extender.get_config().get("use_openai", False)

                if use_openai:
                    layout.show(self._config_panels, "OpenAI")
                    self._openai_radio.setSelected(True)

                    # Ensure button text is correct for OpenAI-compatible
                    openai_url_placeholder = "https://api.openai.com/v1/chat/completions"
                    if hasattr(self, "_toggle_openai_url_button"):
                        openai_url = self._extender.get_config().get("openai_api_url", "")
                        if openai_url and openai_url != openai_url_placeholder:
                            if self._is_openai_url_hidden:
                                self._toggle_openai_url_button.setText("View")
                                self._openai_url_field.setText('*' * len(openai_url))
                            else:
                                self._toggle_openai_url_button.setText("Hide")
                                self._openai_url_field.setText(openai_url)
                        else:
                            self._toggle_openai_url_button.setText("View")
                        self._toggle_openai_url_button.setContentAreaFilled(False)
                        self._toggle_openai_url_button.setBorderPainted(False)
                        self._toggle_openai_url_button.setForeground(Color.GRAY)

                    openai_key_placeholder = "Enter your API Key here..."
                    if hasattr(self, "_toggle_openai_api_key_button"):
                        openai_key = self._extender.get_config().get("openai_api_key", "")
                        if openai_key and openai_key != openai_key_placeholder:
                            if self._is_openai_api_key_hidden:
                                self._toggle_openai_api_key_button.setText("View")
                                self._openai_api_key_field.setText('*' * len(openai_key))
                            else:
                                self._toggle_openai_api_key_button.setText("Hide")
                                self._openai_api_key_field.setText(openai_key)
                        else:
                            self._toggle_openai_api_key_button.setText("View")
                        self._toggle_openai_api_key_button.setContentAreaFilled(False)
                        self._toggle_openai_api_key_button.setBorderPainted(False)
                        self._toggle_openai_api_key_button.setForeground(Color.GRAY)

                elif use_ollama:
                    layout.show(self._config_panels, "Ollama")
                    self._ollama_radio.setSelected(True)

                    # Ensure button text is correct for Ollama
                    if hasattr(self, "_toggle_ollama_url_button"):
                        ollama_url = self._extender.get_config()["ollama_url"]
                        if ollama_url and ollama_url != "":
                            if self._is_ollama_url_hidden:
                                self._toggle_ollama_url_button.setText("View")
                                self._ollama_url_field.setText('*' * len(ollama_url))
                            else:
                                self._toggle_ollama_url_button.setText("Hide")
                                self._ollama_url_field.setText(ollama_url)
                        self._toggle_ollama_url_button.setContentAreaFilled(False)
                        self._toggle_ollama_url_button.setBorderPainted(False)
                        self._toggle_ollama_url_button.setForeground(Color.GRAY)
                else:
                    layout.show(self._config_panels, "OpenRouter")
                    self._openrouter_radio.setSelected(True)

                    # Ensure button text is correct for OpenRouter
                    if hasattr(self, "_toggle_api_key_button"):
                        actual_key = self._extender.get_config()["api_key"]
                        if actual_key and actual_key != "Enter your API Key here...":
                            if self._is_api_key_hidden:
                                self._toggle_api_key_button.setText("View")
                                self._api_key_field.setText('*' * len(actual_key))
                            else:
                                self._toggle_api_key_button.setText("Hide")
                                self._api_key_field.setText(actual_key)
                        else:
                            self._toggle_api_key_button.setText("View")
                        self._toggle_api_key_button.setContentAreaFilled(False)
                        self._toggle_api_key_button.setBorderPainted(False)
                        self._toggle_api_key_button.setForeground(Color.GRAY)

                # Force UI update for the panels
                self._config_panels.revalidate()
                self._config_panels.repaint()

                # Update models in ComboBoxes based on current mode
                if use_openai:
                    # Reset both OpenRouter and Ollama ComboBoxes
                    self._model_combo.setModel(DefaultComboBoxModel(self._extender.get_available_models(False, False)))
                    editor_component = self._model_combo.getEditor().getEditorComponent()
                    if isinstance(editor_component, JTextField):
                        editor_component.setText("Type your model name or fetch the list of available model")

                    self._ollama_model_combo.setModel(DefaultComboBoxModel(self._extender.get_available_models(True, False)))
                    editor_component = self._ollama_model_combo.getEditor().getEditorComponent()
                    if isinstance(editor_component, JTextField):
                        editor_component.setText("Type your model name or fetch the list of available model")

                    # Update OpenAI model field with saved value
                    openai_model = self._extender.get_config().get("openai_model", "")
                    openai_model_placeholder = "Enter your model name (e.g., gpt-4)"
                    if hasattr(self, "_openai_model_field"):
                        if openai_model and openai_model != openai_model_placeholder:
                            self._openai_model_field.setText(openai_model)
                        else:
                            self._openai_model_field.setText(openai_model_placeholder)

                    # Update OpenAI URL field with saved value
                    openai_url = self._extender.get_config().get("openai_api_url", "")
                    openai_url_placeholder = "Enter OpenAI API URL here..."
                    if hasattr(self, "_openai_url_field"):
                        if openai_url:
                            # URL is configured, show it (masked if hidden)
                            if self._is_openai_url_hidden:
                                self._openai_url_field.setText('*' * len(openai_url))
                            else:
                                self._openai_url_field.setText(openai_url)
                        else:
                            self._openai_url_field.setText(openai_url_placeholder)

                    # Update OpenAI API key field with saved value
                    openai_key = self._extender.get_config().get("openai_api_key", "")
                    if hasattr(self, "_openai_api_key_field"):
                        if openai_key:
                            # Key is configured, show it (masked if hidden)
                            if self._is_openai_api_key_hidden:
                                self._openai_api_key_field.setText('*' * len(openai_key))
                            else:
                                self._openai_api_key_field.setText(openai_key)
                        else:
                            self._openai_api_key_field.setText("Enter your API Key here...")

                elif use_ollama:
                    # Reset OpenRouter ComboBox
                    self._model_combo.setModel(DefaultComboBoxModel(self._extender.get_available_models(False, False)))
                    editor_component = self._model_combo.getEditor().getEditorComponent()
                    if isinstance(editor_component, JTextField):
                        editor_component.setText("Type your model name or fetch the list of available model")

                    # Update Ollama combobox
                    ollama_model = self._extender.get_config().get("ollama_model", "")

                    if ollama_model and ollama_model != "Type your model name or fetch the list of available model":
                        model_found = False
                        for i in range(self._ollama_model_combo.getItemCount()):
                            if self._ollama_model_combo.getItemAt(i) == ollama_model:
                                model_found = True
                                break
                        if model_found:
                            self._ollama_model_combo.setSelectedItem(ollama_model)
                        else:
                            model = DefaultComboBoxModel(self._extender.get_available_models(True, False))
                            model.insertElementAt(ollama_model, 0)
                            self._ollama_model_combo.setModel(model)
                            self._ollama_model_combo.setSelectedItem(ollama_model)
                    else:
                        editor_component = self._ollama_model_combo.getEditor().getEditorComponent()
                        if isinstance(editor_component, JTextField):
                            editor_component.setText("Type your model name or fetch the list of available model")

                else:
                    # Reset Ollama ComboBox
                    self._ollama_model_combo.setModel(DefaultComboBoxModel(self._extender.get_available_models(True, False)))
                    editor_component = self._ollama_model_combo.getEditor().getEditorComponent()
                    if isinstance(editor_component, JTextField):
                        editor_component.setText("Type your model name or fetch the list of available model")

                    # Update OpenRouter combobox
                    openrouter_model = self._extender.get_config().get("openrouter_model", "")

                    if openrouter_model and openrouter_model != "Type your model name or fetch the list of available model":
                        model_found = False
                        for i in range(self._model_combo.getItemCount()):
                            if self._model_combo.getItemAt(i) == openrouter_model:
                                model_found = True
                                break
                        if model_found:
                            self._model_combo.setSelectedItem(openrouter_model)
                        else:
                            model = DefaultComboBoxModel(self._extender.get_available_models(False, False))
                            model.insertElementAt(openrouter_model, 0)
                            self._model_combo.setModel(model)
                            self._model_combo.setSelectedItem(openrouter_model)
                    else:
                        editor_component = self._model_combo.getEditor().getEditorComponent()
                        if isinstance(editor_component, JTextField):
                            editor_component.setText("Type your model name or fetch the list of available model")

                # Force visual update of buttons
                if hasattr(self, "_toggle_api_key_button"):
                    self._toggle_api_key_button.repaint()
                if hasattr(self, "_toggle_ollama_url_button"):
                    self._toggle_ollama_url_button.repaint()
                if hasattr(self, "_toggle_openai_url_button"):
                    self._toggle_openai_url_button.repaint()
                if hasattr(self, "_toggle_openai_api_key_button"):
                    self._toggle_openai_api_key_button.repaint()
        except Exception as e:
            # Log the error if available
            try:
                import traceback
                self._extender._callbacks.getStdout().write(
                    "Error updating config panels: " + str(e) + "\n" + traceback.format_exc() + "\n")
            except:
                pass
    
    def update_cache_stats(self):
        """Update cache statistics display in UI"""
        if hasattr(self, "_cache_size_label") and self._cache_size_label:
            cache_stats = self._extender.get_cache_stats()
            
            # Update label text with current size only - no tooltip
            self._cache_size_label.setText("Cache (" + cache_stats["size_str"] + "):")
            
            # Force repaint to ensure the label is updated visually
            self._cache_size_label.revalidate()
            self._cache_size_label.repaint()
    
    def update_api_key_button(self):
        """Force update of API key button"""
        if hasattr(self, "_toggle_api_key_button") and self._toggle_api_key_button:
            if self._is_api_key_hidden:
                self._toggle_api_key_button.setText("View")
            else:
                self._toggle_api_key_button.setText("Hide")
            self._toggle_api_key_button.repaint()
            self._toggle_api_key_button.validate()
    
    def update_model_combo(self, models):
        """
        Update OpenRouter model combo box.
        
        Args:
            models: List of model names
        """
        # Sort models alphabetically
        models.sort()
        new_model = DefaultComboBoxModel(models)
        self._model_combo.setModel(new_model)
        self.update_filter_key_listeners()
    
    def update_ollama_model_combo(self, models):
        """
        Update Ollama model combo box.
        
        Args:
            models: List of model names
        """
        # Sort models alphabetically
        models.sort()
        new_model = DefaultComboBoxModel(models)
        self._ollama_model_combo.setModel(new_model)
        self.update_filter_key_listeners()
    
    def update_filter_key_listeners(self):
        """Update key listeners for model filtering"""
        # Update listeners for OpenRouter models
        editor_component_or = self._model_combo.getEditor().getEditorComponent()
        if isinstance(editor_component_or, JTextField):
            # Delete old listeners
            for listener in editor_component_or.getKeyListeners():
                if isinstance(listener, FilterKeyListener):
                    editor_component_or.removeKeyListener(listener)
            
            # Add a new listener with a complete list of models
            editor_component_or.addKeyListener(FilterKeyListener(self._model_combo, self._extender.get_available_models()))
        
        # Update listeners for Ollama models
        editor_component_ol = self._ollama_model_combo.getEditor().getEditorComponent()
        if isinstance(editor_component_ol, JTextField):
            # Delete old listeners
            for listener in editor_component_ol.getKeyListeners():
                if isinstance(listener, FilterKeyListener):
                    editor_component_ol.removeKeyListener(listener)
            
            # Add a new listener with a complete list of models
            editor_component_ol.addKeyListener(
                FilterKeyListener(self._ollama_model_combo, self._extender.get_available_models(True)))

    def toggle_secret_field(self, field, button, hidden_attr_name, actual_value, placeholder):
        """
        Generic helper for toggling visibility of sensitive fields (URLs, API keys).

        Args:
            field: The JTextField to update
            button: The JButton to update text on
            hidden_attr_name: The attribute name for the hidden state (e.g., "_is_api_key_hidden")
            actual_value: The actual value to show/hide
            placeholder: The placeholder text to ignore
        """
        if not hasattr(self, hidden_attr_name):
            return

        hidden = not getattr(self, hidden_attr_name)
        setattr(self, hidden_attr_name, hidden)

        if not actual_value or actual_value == placeholder:
            button.setText("View" if hidden else "Hide")
            return

        if hidden:
            field.setText('*' * len(actual_value))
            button.setText("View")
        else:
            field.setText(actual_value)
            button.setText("Hide")

        field.revalidate()
        field.repaint()
        button.revalidate()
        button.repaint()