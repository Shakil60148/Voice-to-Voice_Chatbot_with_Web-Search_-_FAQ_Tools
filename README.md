# Voice Assistant with Web Search & FAQ Tools

A complete voice-to-voice chatbot that can transcribe speech, answer questions from a local database, search the web for information, and respond with synthesized speech.

## Features

- **Speech-to-Text**: Convert spoken questions to text using AssemblyAI
- **Question Answering**: 
  - Local FAQ database for common questions
  - Web search capabilities using Tavily's API
- **Text-to-Speech**: Convert answers back to spoken responses
- **User-Friendly Interface**: Easy-to-use Streamlit web interface

## Project Structure

- `voice_assistant.py` - Main application entry point for the voice assistant
- `web_interface.py` - Streamlit web interface for the application
- `answer_agent.py` - Handles question answering from database and web search
- `audio_processing.py` - Functions for audio file processing and transcription
- `speech_recognition.py` - Command-line tool for speech-to-text conversion
- `text_to_speech.py` - Converts text responses to spoken audio
- `qa_database.json` - Local database of frequently asked questions
- `requirements.txt` - Python package dependencies

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   Create a `.env` file in the project root and add your API keys:
   ```
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```
   - Get an AssemblyAI API key from [AssemblyAI](https://www.assemblyai.com/) 
   - Get a Tavily API key from [Tavily](https://tavily.com/)

## Usage

### Voice Assistant Application

```bash
streamlit run voice_assistant.py
```

This launches the complete voice assistant with:
- Speech-to-text conversion
- Question answering from local database
- Web search capabilities
- Text-to-speech responses

### Web Interface Only

```bash
streamlit run web_interface.py
```

### Individual Components

You can also use the individual components:

1. **Speech-to-Text Only**:
   ```bash
   python speech_recognition.py your_audio_file.mp3 --output transcription.txt
   ```

2. **Answer Agent API Usage**:
   ```python
   from answer_agent import AnswerAgent
   
   agent = AnswerAgent()
   response = agent.get_answer("What is a voice assistant?")
   print(response["answer"])
   ```

3. **Text-to-Speech API Usage**:
   ```python
   from text_to_speech import TextToSpeech
   
   tts = TextToSpeech()
   audio_file = tts.text_to_speech("Hello, this is a test.", "output.mp3")
   ```

## How It Works

1. **Speech Recognition**:
   - User uploads or records an audio question
   - AssemblyAI transcribes the speech to text

2. **Question Answering**:
   - System first checks the local FAQ database using fuzzy matching
   - If no match is found, searches the web using Tavily API

3. **Response Generation**:
   - Formats the answer from either source
   - Converts the text answer to speech using gTTS
   - Presents both text and audio to the user

## Customizing the FAQ Database

The local FAQ database is stored in `qa_database.json`. You can edit this file to add, remove, or modify questions and answers. The format is:

```json
{
  "questions": [
    {
      "question": "What is a voice assistant?",
      "answer": "A voice assistant is a digital assistant that uses voice recognition..."
    },
    ...
  ]
}
```

## API Usage and Limits

- **AssemblyAI**: Free tier includes 3 hours of audio processing per month
- **Tavily**: Free tier includes 1000 searches per month

Check the respective websites for current pricing and limits.

## Alternative Speech Recognition Services

If you want to modify the project to use a different speech recognition service, consider:

- Microsoft Azure Speech Services
- Amazon Transcribe
- Deepgram
- Google Speech-to-Text

## Requirements

- Python 3.8+
- Internet connection for web search and speech recognition
- API keys for AssemblyAI and Tavily

## License

[MIT License](https://opensource.org/licenses/MIT)
