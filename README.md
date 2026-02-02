<h1 align="center">AI Request Analyzer</h1>

<p align="center">
  <img src=".github/images/Logo Portswigger.png" alt="PortSwigger Logo" width="150">
</p>

<p align="center">A Burp Suite extension for analyzing HTTP requests and responses with AI. <br> This extension allows security testers to quickly analyze requests for potential vulnerabilities and understand complex responses.</p>

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## ✨ Features

- Analyze HTTP requests for security issues with "AI Suggest" tab
- Understand HTTP responses with the "AI Explain" tab
- Support for multiple AI providers:
  - **OpenRouter** - Access to Claude, GPT-4, and many other models
  - **Ollama** - Run models locally without API keys
  - **OpenAI-compatible** - Use any OpenAI-compatible API (OpenAI, Groq, z.ai GLM, DeepSeek, etc.)
- Caching system to avoid repeated analysis of identical requests
- Configurable prompt templates
- Streaming responses with real-time feedback
- Support for reasoning models (GLM, DeepSeek-R1)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 🔧 Installation

1. Download the extension files
2. In Burp Suite, go to Extensions > Add
3. Select the main.py file as the Python extension entry point
4. The extension will appear as a new tab called "AI Request Analyzer"

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## ⚙️ Configuration

The extension supports three AI providers:

### OpenRouter
- Requires an API key (get one from [openrouter.ai](https://openrouter.ai))
- Supports a wide range of powerful models like Claude, GPT, etc.
- Select a model from the list after fetching available models
- For best results, prefer "instruct" models
- Can be configured via UI or `.env` file (`OPENROUTER_API_KEY`, `OPENROUTER_DEFAULT_MODEL`)

### Ollama
- Requires a local Ollama installation (get from [ollama.ai](https://ollama.ai))
- Run models locally with no API keys needed
- Enter your Ollama URL (default: http://localhost:11434/api/generate)
- Click "Fetch Models" to see available models on your Ollama server
- Can be configured via UI or `.env` file (`OLLAMA_API_URL`, `OLLAMA_DEFAULT_MODEL`)

### OpenAI-compatible
- Use any OpenAI-compatible API endpoint
- Supports: OpenAI, Groq, z.ai GLM, DeepSeek, Together AI, etc.
- Configure in UI or via `.env` file:
  - **API URL**: The endpoint URL (e.g., `https://api.openai.com/v1/chat/completions`)
  - **API Key**: Your API key for the service
  - **Model Name**: The model to use (e.g., `gpt-4`, `claude-3-opus-20240229`, `glm-4`)
- No "Fetch Models" button - enter the model name manually
- Supports reasoning models like GLM and DeepSeek-R1 (only shows final answer, not reasoning)

### 🔧 Environment Variables (.env)

The extension can be configured via environment variables using a `.env` file:

1. Copy `.env-dist` to `.env` to start using environment variables
2. Edit the `.env` file with your API keys and preferences
3. Environment variables are used as **defaults** when Burp settings are empty
4. Once loaded from `.env`, values are saved to Burp settings for persistence

**Note**: You can also configure everything through the Burp Suite UI without using `.env` files.

If no `.env` file is found, the extension will use these default values:

```
# Cache configuration
CACHE_MAX_SIZE_MB=100      # Maximum cache size in MB
CACHE_MAX_AGE_DAYS=30      # Maximum days to keep cache entries
CACHE_MAX_ENTRIES=1000     # Maximum number of cache entries

# Message configuration
MAX_MESSAGE_LENGTH=4000    # Maximum length before truncating HTTP messages

# OpenRouter configuration
OPENROUTER_MAX_TOKENS=800  # Maximum tokens for OpenRouter responses
OPENROUTER_API_URL=        # Custom API URL (leave empty for default)
OPENROUTER_API_KEY=         # API key for OpenRouter
OPENROUTER_DEFAULT_MODEL=  # Default model to use (leave empty to select manually)
OPENROUTER_TEMPERATURE=0.3 # Temperature for response generation (0.0-1.0)

# Ollama configuration
OLLAMA_API_URL=            # Custom API URL (leave empty for default)
OLLAMA_DEFAULT_MODEL=      # Default model to use (leave empty to select manually)
OLLAMA_TEMPERATURE=0.3     # Temperature for response generation (0.0-1.0)

# OpenAI-compatible configuration
OPENAI_API_URL=            # Custom API URL (e.g., https://api.openai.com/v1/chat/completions)
OPENAI_API_KEY=            # API key for the service
OPENAI_DEFAULT_MODEL=      # Default model to use (e.g., gpt-4, claude-3-opus-20240229)
OPENAI_TEMPERATURE=0.3     # Temperature for response generation (0.0-1.0)
```

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 🚀 Usage

1. Configure your preferred AI provider in the "AI Request Analyzer" tab
2. Browse the application you're testing in Burp Suite
3. When you find an interesting request:
   - Use the "AI Suggest" tab to get vulnerability suggestions for that request
   - Use the "AI Explain" tab to understand complex responses
4. Enable/disable automatic analysis in the options panel
5. Clear the cache as needed

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 💡 Tips

- After fetching models, you can type keywords to filter them:
  - "claude" for Claude models
  - "gpt" for GPT models
  - "free" for models without credit requirements in OpenRouter
- "Instruct" models typically provide better security-focused responses
- Large HTTP messages are automatically truncated to save tokens
- Analysis results are cached to improve performance
- You can customize the prompts in the "AI Request Analyzer" tab

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 📝 Customizing Prompts

The extension uses prompt templates to guide the AI in analyzing requests and responses. There are two ways to customize these prompts:

1. **Temporary Customization (UI):**
   - You can modify prompts directly in the "AI Request Analyzer" tab
   - These changes apply immediately but are not persistent
   - Changes will be lost when Burp Suite is restarted

2. **Permanent Customization (Files):**
   - For persistent custom prompts, modify the text files in the `prompts/` directory:
     - `suggest_prompt.txt`: Template for request vulnerability suggestions
     - `explain_prompt.txt`: Template for response analysis
   - These files are loaded each time the extension starts
   - Changes to these files will persist across Burp Suite restarts

When customizing prompts, focus on providing clear instructions for the AI about what to analyze and how to format the results.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 👨‍💻 Development

- This extension is written in Python for Burp Suite's Jython environment
- The project uses a modular architecture
- Contribute via issues and pull requests

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

## 📂 Structure

The project is organized into the following modules:

- **main.py**: Main extension entry point
- **core/**: Core functionality
  - **api_handlers.py**: API communication with OpenRouter, Ollama, and OpenAI-compatible APIs
  - **cache.py**: Caching system with performance optimizations
  - **config_loader.py**: Configuration and .env file handling
  - **models.py**: Model management
- **ui/**: UI components and layout
  - **analyzer_tabs.py**: Request and response analysis tabs
  - **config_tab.py**: Configuration tab interface
  - **components.py**: Reusable UI components
- **utils/**: Utility functions
  - **helpers.py**: Helper functions
  - **listeners.py**: Event listeners
  - **prompt_manager.py**: Prompt template management
  - **settings.py**: Settings handling
- **prompts/**: Template prompts for different analysis types
  - **explain_prompt.txt**: Template for response analysis
  - **suggest_prompt.txt**: Template for request vulnerability suggestions

## 📄 License

This project is open source and available under the MIT License.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)