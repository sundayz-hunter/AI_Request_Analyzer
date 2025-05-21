# -*- coding: utf-8 -*-

import json
import urllib2
import traceback
import time

# Error message constants
FREE_TIER_LIMIT_MESSAGE = "FREE TIER LIMIT REACHED\n\nYou've reached the daily limit for free models on OpenRouter.\n\nOptions:\n1. Wait for quota reset\n2. Try a paid model\n3. Add credits to your account\n4. Switch to Ollama"
RATE_LIMIT_MESSAGE = "RATE LIMIT EXCEEDED\n\nOpenRouter API rate limit reached:\n\n{0}\n\nPlease try again later or switch to a different model."
OPENROUTER_ERROR_MESSAGE = "Error: OpenRouter API returned an error:\n\n{0}"
DEFAULT_HTTP_ERROR_MESSAGE = "HTTP Error {0} when connecting to OpenRouter.\nPlease check your API key and model selection."
FALLBACK_ERROR_MESSAGE = "Error: Could not get a valid response from OpenRouter."
STREAMING_FALLBACK_ERROR_MESSAGE = "Error: Both streaming and non-streaming requests failed."
OLLAMA_ERROR_MESSAGE = "Error connecting to Ollama (stream): {0}\n\nCheck that the Ollama server is running at: {1}\n\nAlternative: try switching to OpenRouter which has better compatibility with Burp Suite."

class BaseAPIHandler:
    """
    Base class for API handlers, providing common functionality
    for different AI providers.
    """
    
    def __init__(self, extender):
        """
        Initialize the API handler.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
        self._stdout = extender._callbacks.getStdout()


class OpenRouterHandler(BaseAPIHandler):
    """
    Handles API communication with OpenRouter.
    """
    
    def analyze_message(self, message, is_request, update_callback):
        """
        Analyze a message using OpenRouter API.
        
        Args:
            message: The message content
            is_request: Whether the message is a request or response
            update_callback: Callback function to update the UI with progress/results
            
        Returns:
            Analysis result text
        """
        config = self._extender.get_config()
        api_key = config["api_key"]
        model = config["model"]
        
        # Limit message size to prevent excessive token usage
        max_message_length = config.get("MAX_MESSAGE_LENGTH", 4000)
        message_str = self._extender._helpers.bytesToString(message)
        
        # Use the truncate function from helpers
        short_message = self._extender.truncate_message(message_str, max_message_length)
        
        # Set appropriate prompt based on message type
        if is_request:
            system_prompt = self._extender.get_config().get("suggest_prompt", "")
            user_prompt = "Analyze this HTTP request for security issues:\n\n" + short_message
        else:
            system_prompt = self._extender.get_config().get("explain_prompt", "")
            user_prompt = "Analyze this HTTP response:\n\n" + short_message
        
        # OpenRouter API call (streaming mode)
        openrouter_url = config.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
        openrouter_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }
        
        # Build payload with streaming mode
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": config.get("OPENROUTER_TEMPERATURE", 0.3),
            "max_tokens": config.get("OPENROUTER_MAX_TOKENS", 800),
            "stream": True
        }
        
        # Initial message
        update_callback("Analysis in progress...")
        
        # Minimal debug info
        self._stdout.write("Sending request to OpenRouter API (streaming mode)\n")
        self._stdout.write("Model: " + model + "\n")
        
        # Convert to JSON
        data = json.dumps(payload)
        
        try:
            # Make request
            req = urllib2.Request(openrouter_url, data, openrouter_headers)
            response = urllib2.urlopen(req, timeout=120)
            
            # Character-by-character strategy for OpenRouter - ultra responsive
            full_response = ""
            chunk_count = 0
            last_update_time = time.time()
            
            for line in response:
                chunk_count += 1
                line = line.strip()
                
                if not line or line == "data: [DONE]":
                    continue
                
                if line.startswith("data: "):
                    json_str = line[6:]
                    
                    if json_str == "{}":
                        continue
                    
                    try:
                        chunk_data = json.loads(json_str)
                        
                        if "choices" in chunk_data and chunk_data["choices"] and "delta" in chunk_data["choices"][0]:
                            delta = chunk_data["choices"][0]["delta"]
                            if "content" in delta:
                                content_chunk = delta["content"]
                                if content_chunk:
                                    full_response += content_chunk
                                    
                                    # Update UI frequently for responsive feedback
                                    current_time = time.time()
                                    time_since_last_update = current_time - last_update_time
                                    
                                    if chunk_count <= 20 or time_since_last_update >= 0.1:
                                        update_callback(full_response)
                                        last_update_time = current_time
                    except:
                        pass
            
            # Final update
            if full_response:
                update_callback(full_response)
                self._stdout.write("OpenRouter analysis complete - processed {0} chunks.\n".format(chunk_count))
                return full_response
            else:
                # Log that no content was received
                self._stdout.write("No content received from streaming. Trying fallback...\n")
                update_callback("Analyzing with OpenRouter...")
                
                # Try fallback to non-streaming mode
                return self._fallback_to_non_streaming(openrouter_url, openrouter_headers, payload, update_callback)
        
        except urllib2.HTTPError as e:
            # Handle HTTP errors (like 429 rate limits)
            error_message = self._handle_openrouter_error(e)
            update_callback(error_message)
            return error_message
        except Exception as e:
            self._stdout.write("Error processing OpenRouter request: " + str(e) + "\n")
            
            # Check if it's a rate limit or quota error message
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                error_message = FREE_TIER_LIMIT_MESSAGE
            else:
                error_message = "Error: " + str(e)
            
            update_callback(error_message)
            return error_message
    
    def _handle_openrouter_error(self, error):
        """
        Handle HTTP errors from OpenRouter API with special handling for rate limits.
        
        Args:
            error: The HTTP error
            
        Returns:
            Error message to display
        """
        # Get the error response body if possible
        error_body = error.read() if hasattr(error, 'read') else ""
        self._stdout.write("HTTP Error: " + str(error.code) + " - " + str(error.reason) + "\n")
        self._stdout.write("Error body: " + error_body + "\n")
        
        # Try to parse error as JSON
        try:
            error_json = json.loads(error_body)
            
            # Special handling for rate limit errors (429)
            if error.code == 429 and "error" in error_json:
                error_info = error_json["error"]
                
                # Check if it's specifically about free tier limits
                if isinstance(error_info, dict) and "message" in error_info and "free-models-per-day" in error_info["message"]:
                    # This is a free tier rate limit
                    return FREE_TIER_LIMIT_MESSAGE
                
                # Generic rate limit error
                return RATE_LIMIT_MESSAGE.format(str(error_info))
            
            # For other types of errors
            if "error" in error_json:
                error_info = str(error_json["error"])
                return OPENROUTER_ERROR_MESSAGE.format(error_info)
        
        except:
            # If can't parse JSON or other error
            pass
        
        # Default error handling
        return DEFAULT_HTTP_ERROR_MESSAGE.format(str(error.code))
    
    def _fallback_to_non_streaming(self, url, headers, payload, update_callback):
        """
        Fallback to non-streaming mode if streaming fails.
        
        Args:
            url: The API URL
            headers: Request headers
            payload: Request payload
            update_callback: Callback function to update the UI
            
        Returns:
            Analysis result text
        """
        try:
            self._stdout.write("Falling back to non-streaming mode\n")
            
            # Modify payload to disable streaming
            payload_copy = dict(payload)
            payload_copy["stream"] = False
            
            # Convert to JSON
            data = json.dumps(payload_copy)
            
            # Make request
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req, timeout=120)
            
            # Parse response
            response_data = response.read()
            self._stdout.write("Fallback response received: " + str(len(response_data)) + " bytes\n")
            
            response_json = json.loads(response_data)
            
            # Extract content
            if "choices" in response_json and response_json["choices"] and "message" in response_json["choices"][0]:
                message = response_json["choices"][0]["message"]
                if "content" in message:
                    content = message["content"]
                    update_callback(content)
                    self._stdout.write("Fallback request successful\n")
                    return content
            
            # Check for error information in the response
            if "error" in response_json:
                error_info = response_json["error"]
                
                # Check for rate limit message
                if isinstance(error_info, dict) and "message" in error_info:
                    error_message = error_info["message"]
                    
                    # Check for free tier limit message
                    if "free-models-per-day" in error_message:
                        update_callback(FREE_TIER_LIMIT_MESSAGE)
                        return FREE_TIER_LIMIT_MESSAGE
                    
                    # Other rate limit error
                    if "rate limit" in error_message.lower() or "rate-limit" in error_message.lower():
                        error_text = RATE_LIMIT_MESSAGE.format(str(error_info))
                        update_callback(error_text)
                        return error_text
                
                # Generic error
                error_text = "Error: " + str(error_info)
                update_callback(error_text)
                return error_text
            
            # If couldn't extract content
            self._stdout.write("Failed to extract content from fallback response\n")
            update_callback(FALLBACK_ERROR_MESSAGE)
            return FALLBACK_ERROR_MESSAGE
        
        except urllib2.HTTPError as e:
            # For HTTP errors, try to extract the error info
            error_message = self._handle_openrouter_error(e)
            update_callback(error_message)
            return error_message
        
        except Exception as e:
            self._stdout.write("Fallback request failed: " + str(e) + "\n")
            update_callback(STREAMING_FALLBACK_ERROR_MESSAGE)
            return STREAMING_FALLBACK_ERROR_MESSAGE
            
    def fetch_available_models(self, on_complete):
        """
        Fetch available models from OpenRouter.
        
        Args:
            on_complete: Callback function to call when models are fetched
        """
        # OpenRouter API URL for models
        config = self._extender.get_config()
        models_url = config.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
        
        # Remove /chat/completions if present and add /models
        if models_url.endswith("/chat/completions"):
            models_url = models_url[:-len("/chat/completions")]
        
        models_url = models_url + "/models"
        
        api_key = config["api_key"]
        
        if not api_key or api_key == "Enter your API Key here...":
            on_complete([], "Error: API key not configured.")
            return
        
        # Headers with API key
        headers = {
            "Authorization": "Bearer " + api_key
        }
        
        try:
            # Make request to fetch models
            req = urllib2.Request(models_url, headers=headers)
            response = urllib2.urlopen(req, timeout=30)
            
            # Parse response
            response_data = response.read()
            models_json = json.loads(response_data)
            
            # Extract model IDs
            model_ids = []
            if "data" in models_json:
                for model in models_json["data"]:
                    if "id" in model:
                        model_ids.append(model["id"])
            
            # Sort model IDs
            model_ids.sort()
            
            # Pass models to callback
            on_complete(model_ids)
        except Exception as e:
            self._stdout.write("Error fetching models from OpenRouter: " + str(e) + "\n")
            on_complete([], "Error: " + str(e))


class OllamaHandler(BaseAPIHandler):
    """
    Handles API communication with Ollama.
    """
    
    def analyze_message(self, message, is_request, update_callback):
        """
        Analyze a message using Ollama API.
        
        Args:
            message: The message content
            is_request: Whether the message is a request or response
            update_callback: Callback function to update the UI with progress/results
            
        Returns:
            Analysis result text
        """
        config = self._extender.get_config()
        model = config["model"]
        ollama_url = config.get("ollama_url", "")
        
        # Check if URL is configured
        if not ollama_url or ollama_url.strip() == "":
            error_text = "Error: Ollama URL not configured. Please enter the Ollama URL in the AI Request Analyzer tab."
            update_callback(error_text)
            return error_text
        
        # Limit message size to prevent excessive token usage
        max_message_length = config.get("MAX_MESSAGE_LENGTH", 4000)
        message_str = self._extender._helpers.bytesToString(message)
        
        # Use the truncate function from helpers
        short_message = self._extender.truncate_message(message_str, max_message_length)
        
        # Prepare simple prompt to reduce encoding errors risk
        simple_prompt = "Analyze the following for security issues. Keep your answer simple and in ASCII:\n\n"
        simple_prompt += short_message[:2000]  # Limit size
        
        # Ollama API headers
        ollama_headers = {"Content-Type": "application/json"}
        
        # Prepare payload with stream=True
        ollama_payload = {
            "model": model.split("/")[-1] if "/" in model else model,
            "prompt": simple_prompt,
            "stream": True,
            "temperature": config.get("OLLAMA_TEMPERATURE", 0.3)
        }
        
        # Convert to JSON
        data = json.dumps(ollama_payload).encode('utf-8')
        
        # Convert to native Python types (important in Jython)
        ollama_url = str(ollama_url)
        ollama_headers = dict(ollama_headers)
        
        try:
            header_text = ""
            self._stdout.write("Sending streaming request to Ollama\n")
            req = urllib2.Request(ollama_url, data, ollama_headers)
            response = urllib2.urlopen(req, timeout=90)
            
            # Line-by-line reading (stream)
            full_response = ""
            chunk_count = 0
            last_update_time = time.time()
            for line in response:
                chunk_count += 1
                line = line.strip()
                if not line:
                    continue
                try:
                    # Each line is a JSON with a 'response' field
                    chunk_json = json.loads(line)
                    if "response" in chunk_json:
                        content_chunk = chunk_json["response"]
                        if content_chunk:
                            full_response += content_chunk
                            # Progressive update (every 0.1s or first 20 chunks)
                            current_time = time.time()
                            if chunk_count <= 20 or current_time - last_update_time >= 0.1:
                                update_callback(header_text + full_response)
                                last_update_time = current_time
                except Exception as e:
                    self._stdout.write("Ollama stream chunk error: " + str(e) + "\n")
                    continue
            
            # Final update
            if full_response:
                update_callback(header_text + full_response)
                self._stdout.write("Ollama streaming complete - processed {0} chunks.\n".format(chunk_count))
                return header_text + full_response
            else:
                error_text = header_text + "No response received from Ollama."
                update_callback(error_text)
                return error_text
        
        except Exception as e:
            self._stdout.write("Global Ollama streaming error: " + str(e) + "\n")
            error_text = OLLAMA_ERROR_MESSAGE.format(str(e), ollama_url)
            update_callback(error_text)
            return error_text
    
    def fetch_available_models(self, on_complete):
        """
        Fetch available models from Ollama using Java's native HTTP implementation.
        
        Args:
            on_complete: Callback function to call when models are fetched
        """
        # Import Java classes for HTTP
        from java.net import URL, HttpURLConnection
        from java.io import BufferedReader, InputStreamReader
        from java.lang import StringBuilder, String
        from java.nio.charset import StandardCharsets

        config = self._extender.get_config()
        ollama_url = config.get("ollama_url", "")
        
        # Check if URL is configured
        if not ollama_url or ollama_url.strip() == "":
            on_complete([], "Error: Ollama URL not configured.")
            return
        
        # Get the base URL (remove /api/generate if present)
        base_url = ollama_url
        if base_url.endswith("/api/generate"):
            base_url = base_url[:-len("/api/generate")]
        
        # Models endpoint
        models_url = base_url + "/api/tags"
        
        try:
            # Using Java classes to avoid buffer problems
            url = URL(models_url)
            connection = url.openConnection()
            
            # Setting up the connection
            connection.setRequestMethod("GET")
            connection.setConnectTimeout(30000)  # 30 secondes
            connection.setReadTimeout(30000)     # 30 secondes
            
            # Read the response (using a Java BufferedReader)
            response_code = connection.getResponseCode()
            
            if response_code == HttpURLConnection.HTTP_OK:
                # Read the response with a StringBuilder (more efficient than String+)
                reader = BufferedReader(InputStreamReader(connection.getInputStream(), "UTF-8"))
                response_text = StringBuilder()
                
                line = reader.readLine()
                while line is not None:
                    response_text.append(line)
                    line = reader.readLine()
                
                reader.close()
                
                # Processing JSON
                try:
                    # Cchange StringBuilder to string
                    response_str = str(response_text.toString())
                    
                    # Parse JSON response
                    models_json = json.loads(response_str)
                    
                    # Extract model names
                    model_names = []
                    if "models" in models_json:
                        for model in models_json["models"]:
                            if "name" in model:
                                try:
                                    model_name = str(model["name"])
                                    model_names.append(model_name)
                                except:
                                    pass
                    
                    # Sort model names
                    model_names.sort()
                    
                    # Callback models
                    on_complete(model_names)
                except Exception as json_err:
                    on_complete([], "Error parsing models: " + str(json_err))
            else:
                on_complete([], "HTTP Error: " + str(response_code))
        except Exception as e:
            on_complete([], "Connection error: " + str(e))