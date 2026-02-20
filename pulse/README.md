# Groot AI Ecosystem

**Groot AI** is a high-performance personal AI assistant designed to optimize context management while providing multimodal interaction. It integrates **ScaleDown** for context pruning and **OpenRouter** for versatile LLM access.

## Features

- **🧠 Context Optimization**: Uses [ScaleDown](https://scaledown.ai) to reduce token usage by 40-60%.
- **🗣️ Multimodal**: Voice interaction (Whisper STT + TTS) and Web Chat (Streamlit).
- **🔌 Model Flexibility**: Compatible with any model via OpenRouter (Claude, Llama, GPT-4).
- **🔒 Privacy**: Local encrypted conversation storage.

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR
   pip install requests cryptography streamlit SpeechRecognition openai-whisper pyttsx3 pyaudio
   ```

2. **Configuration**:
   Groot AI uses environment variables or a `config.py` default.
   Set the following keys (optional if using defaults/free models):
   ```bash
   export SCALEDOWN_API_KEY="your_key"
   export OPENROUTER_API_KEY="your_key"
   ```

## Usage

### Web Interface
Start the chat UI:
```bash
streamlit run pulse/app.py
```

### Voice Assistant
Start the voice loop:
```bash
python pulse/main.py --mode voice
```

## Architecture

- **Brain**: Central logic orchestrating Memory, ScaleDown, and LLM.
- **Memory**: SQLite database with encryption support.
- **ScaleDown**: Context compression service.

## License

MIT
