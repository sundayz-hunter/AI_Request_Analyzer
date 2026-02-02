# -*- coding: utf-8 -*-

from burp import IMessageEditorTab, IMessageEditorController, IMessageEditorTabFactory
from javax.swing import JPanel, JButton, Box, BorderFactory, UIManager, JScrollPane, BoxLayout, SwingUtilities
from java.awt import BorderLayout, Dimension
from java.lang import Runnable, Thread, System
import threading
import time

from utils.listeners import ReloadAnalysisListener

class BaseAnalyzerTab(IMessageEditorTab, IMessageEditorController):
    """
    Base class for analyzer tabs that provides common functionality
    for both request and response tabs.
    """
    
    def __init__(self, extender, controller, editable, is_request):
        """
        Initialize the analyzer tab.
        
        Args:
            extender: The main extender object
            controller: The message editor controller
            editable: Whether the tab is editable
            is_request: Whether this tab analyzes requests (True) or responses (False)
        """
        self._extender = extender
        self._controller = controller
        self._editable = editable
        self._is_request = is_request
        
        # Get stdout for debugging
        self._stdout = extender._callbacks.getStdout()
        
        # Create a panel to host our components
        self._panel = JPanel(BorderLayout())
        
        # Create a panel for the reload button
        button_panel = JPanel()
        button_panel.setLayout(BoxLayout(button_panel, BoxLayout.X_AXIS))
        button_panel.setOpaque(False)
        button_panel.setBorder(BorderFactory.createEmptyBorder(2, 0, 2, 0))  # Reduced vertical margin
        
        # Add a flexible space before the button to center it
        button_panel.add(Box.createHorizontalGlue())
        
        # Create a button with integrated style
        self._reload_button = JButton("Run a new analysis")
        self._reload_button.addActionListener(ReloadAnalysisListener(self))
        self._reload_button.setPreferredSize(Dimension(150, 25))  # Reduced height
        
        # Apply style that matches Burp's appearance
        try:
            self._reload_button.setBorder(BorderFactory.createEmptyBorder(1, 10, 1, 10))
            self._reload_button.setFont(UIManager.getFont("Button.font"))
            self._reload_button.setFocusPainted(False)
        except:
            pass
        button_panel.add(self._reload_button)
        
        # Add a flexible space after the button to center it
        button_panel.add(Box.createHorizontalGlue())
        
        # Add button panel
        self._panel.add(button_panel, BorderLayout.NORTH)
        
        # Use the callbacks.createTextEditor()
        # This method creates a text editor without additional tabs
        self._text_editor = extender._callbacks.createTextEditor()
        self._text_editor.setEditable(False)
        
        # Add the text editor to the panel
        self._editor_component = self._text_editor.getComponent()
        self._panel.add(self._editor_component, BorderLayout.CENTER)
        
        # State variables
        self._current_message = None
        self._current_message_hash = None
        self._lock = threading.Lock()
        self._analysis_complete = False
    
    # IMessageEditorController implementation
    def getHttpService(self):
        return self._controller.getHttpService() if self._controller else None
    
    def getRequest(self):
        return self._controller.getRequest() if self._controller else None
    
    def getResponse(self):
        return self._controller.getResponse() if self._controller else None
    
    def getUiComponent(self):
        return self._panel
    
    def isEnabled(self, content, is_request):
        return content is not None and is_request == self._is_request
    
    # Use the helper function from utils for hashing
    def _calculate_hash(self, content):
        """
        Calculate a hash of the message for caching.
        
        Args:
            content: The message content
            
        Returns:
            A string hash identifier
        """
        # Use the centralized hashing function from helpers.py
        from utils.helpers import calculate_message_hash
        return calculate_message_hash(content)
    
    def setMessage(self, content, is_request):
        """
        Set the message to be displayed/analyzed in the tab.
        
        Args:
            content: The message content
            is_request: Whether it's a request or response
        """
        if content is None:
            self._text_editor.setText(None)
            self._current_message = None
            self._current_message_hash = None
            return
        
        # Check that the message type matches the tab type
        if is_request != self._is_request:
            return
        
        new_hash = self._calculate_hash(content)
        
        # If it's a new message, reset status
        if new_hash != self._current_message_hash:
            self._current_message = content
            self._current_message_hash = new_hash
            self._analysis_complete = False
            
            # Check if we already have a cached analysis
            cached_result = self._extender.get_cached_analysis(new_hash, is_request)
            if cached_result:
                self._stdout.write("Found cached analysis for message hash: {0}\n".format(new_hash))
                # Convert cached text to bytes
                cached_bytes = self._extender._helpers.stringToBytes(cached_result)
                self._text_editor.setText(cached_bytes)
                self._analysis_complete = True
            else:
                # Check if automatic analysis is enabled
                if self._extender.get_config().get("analyze_automatically", True):
                    # Start background analysis
                    thread = threading.Thread(target=self.analyze)
                    thread.daemon = True
                    thread.start()
                else:
                    # Simple message for manual analysis
                    prompt_bytes = self._extender._helpers.stringToBytes("Run an analysis")
                    self._text_editor.setText(prompt_bytes)
        
        return
    
    def analyze(self):
        """
        Start the analysis process for the current message.
        """
        # Reset current analysis state
        self._analysis_complete = False
        
        # Initial message to indicate analysis is starting
        self._update_text_safely("Starting analysis...")
        
        # Start the analysis in a background thread
        thread = threading.Thread(target=self._perform_analysis)
        thread.daemon = True
        thread.start()
        
        # Log the analysis request
        if self._current_message:
            self._stdout.write("Analysis request started for message hash: {0}\n".format(self._current_message_hash))
    
    # Update UI safely
    def _update_text_safely(self, text):
        """
        Update the text editor with new text, ensuring it happens on the Event Dispatch Thread.
        
        Args:
            text: The text to display
        """
        try:
            # Convert text to bytes for the text editor
            text_bytes = self._extender._helpers.stringToBytes(text)
            
            # Create a runnable to update the UI on the Event Dispatch Thread
            class EditorUpdater(Runnable):
                def __init__(self, editor, message):
                    self.editor = editor
                    self.message = message
                
                def run(self):
                    try:
                        # Clear editor before setting new text
                        self.editor.setText(None)
                        # Set new text
                        self.editor.setText(self.message)
                    except Exception as e:
                        # Log any errors that occur during UI update
                        print("Error updating editor: " + str(e))
            
            # Update the editor on the EDT
            SwingUtilities.invokeLater(EditorUpdater(self._text_editor, text_bytes))
            
            # If we have a valid hash and text, cache the result
            if text and self._current_message_hash:
                self._extender.set_cached_analysis(self._current_message_hash, self._is_request, text)
        except Exception as e:
            # In case of buffer errors, use a more direct approach
            try:
                self._stdout.write("Error in _update_text_safely: " + str(e) + "\n")
                # Direct approach to update text
                self._text_editor.setText(None)  # Clear first
                
                # Create a new byte string from the text
                safe_bytes = self._extender._helpers.stringToBytes("Update error: " + str(e) + "\n\n" + text)
                
                # Update directly
                SwingUtilities.invokeLater(lambda: self._text_editor.setText(safe_bytes))
            except:
                # If all else fails, display a minimal message
                self._text_editor.setText(self._extender._helpers.stringToBytes("Error displaying content"))
    
    def _perform_analysis(self):
        """
        Perform the analysis using the appropriate API handler.
        """
        with self._lock:
            if not self._current_message:
                self._update_text_safely("No message to analyze.")
                return
            
            # Show initial message
            self._update_text_safely("Analysis in progress...")
            
            try:
                # Use the right API manager for your configuration
                config = self._extender.get_config()
                use_ollama = config.get("use_ollama", False)
                use_openai = config.get("use_openai", False)

                # Check configuration before continuing
                if use_openai:
                    # Checks for OpenAI-compatible
                    openai_api_url = config.get("openai_api_url", "")
                    openai_api_key = config.get("openai_api_key", "")
                    openai_model = config.get("openai_model", "")

                    if not openai_api_url or openai_api_url.strip() == "":
                        self._update_text_safely("Error: OpenAI-compatible API URL not configured. Please enter the URL in the AI Request Analyzer tab.")
                        return

                    if not openai_api_key or openai_api_key.strip() == "":
                        self._update_text_safely("Error: OpenAI-compatible API key not configured. Please enter your API key in the AI Request Analyzer tab.")
                        return

                    if not openai_model or openai_model.strip() == "":
                        self._update_text_safely("Error: OpenAI-compatible model not configured. Please enter the model name in the AI Request Analyzer tab.")
                        return
                elif use_ollama:
                    model = config.get("model", "")
                    ollama_url = config.get("ollama_url", "")

                    if not model or model == "Type your model name or fetch the list of available model":
                        self._update_text_safely("Error: No Ollama model selected. Please configure a model in the AI Request Analyzer tab.")
                        return

                    if not ollama_url:
                        self._update_text_safely("Error: Ollama URL not configured. Please enter the Ollama URL in the AI Request Analyzer tab.")
                        return
                else:
                    # Checks for OpenRouter
                    api_key = config.get("api_key", "")
                    model = config.get("model", "")

                    if not api_key or api_key == "Enter your API Key here...":
                        self._update_text_safely("Error: OpenRouter API key not configured. Please enter your API key in the AI Request Analyzer tab.")
                        return

                    if not model or model == "Type your model name or fetch the list of available model":
                        self._update_text_safely("Error: OpenRouter model not selected. Please choose a model in the AI Request Analyzer tab.")
                        return

                # Get the API manager for the current mode
                api_handler = self._extender.get_api_handler(use_ollama, use_openai)
                
                # Analyze the message
                result = api_handler.analyze_message(
                    self._current_message,
                    self._is_request,
                    self._update_text_safely
                )
                
                # Mark analysis complete
                self._analysis_complete = True
            
            except Exception as e:
                self._stdout.write("Exception in analysis: " + str(e) + "\n")
                import traceback
                traceback_str = traceback.format_exc()
                self._stdout.write(traceback_str + "\n")
                self._update_text_safely("Error during analysis: " + str(e) + "\n\nCheck Burp's extension output for details.")
    
    def getMessage(self):
        return self._current_message
    
    def isModified(self):
        return False
    
    def getSelectedData(self):
        return self._text_editor.getSelectedText()


class RequestAnalyzerTab(BaseAnalyzerTab):
    """
    Tab for analyzing HTTP requests and suggesting security tests.
    """
    
    def __init__(self, extender, controller, editable):
        """
        Initialize the request analyzer tab.
        
        Args:
            extender: The main extender object
            controller: The message editor controller
            editable: Whether the tab is editable
        """
        BaseAnalyzerTab.__init__(self, extender, controller, editable, True)
    
    def getTabCaption(self):
        return "AI Suggest"


class ResponseAnalyzerTab(BaseAnalyzerTab):
    """
    Tab for analyzing HTTP responses and explaining their contents.
    """
    
    def __init__(self, extender, controller, editable):
        """
        Initialize the response analyzer tab.
        
        Args:
            extender: The main extender object
            controller: The message editor controller
            editable: Whether the tab is editable
        """
        BaseAnalyzerTab.__init__(self, extender, controller, editable, False)
    
    def getTabCaption(self):
        return "AI Explain"


# Factory class for response tabs
class ResponseTabFactory(IMessageEditorTabFactory):
    """
    Factory for creating response analyzer tabs.
    Implements IMessageEditorTabFactory interface.
    """
    
    def __init__(self, extender):
        """
        Initialize the factory.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
    
    def createNewInstance(self, controller, editable):
        """
        Create a new response analyzer tab.
        
        Args:
            controller: The message editor controller
            editable: Whether the tab is editable
            
        Returns:
            A new ResponseAnalyzerTab instance
        """
        return ResponseAnalyzerTab(self._extender, controller, editable)
