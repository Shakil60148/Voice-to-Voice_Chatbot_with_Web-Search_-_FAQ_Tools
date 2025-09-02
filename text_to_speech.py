import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self, language='en', slow=False):
        """
        Initialize the Text to Speech engine
        
        Args:
            language: Language code (default: 'en' for English)
            slow: Whether to speak slowly (default: False)
        """
        self.language = language
        self.slow = slow
    
    def text_to_speech(self, text, output_file=None):
        """
        Convert text to speech
        
        Args:
            text: The text to convert to speech
            output_file: The path to save the audio file (if None, a temporary file is used)
            
        Returns:
            The path to the generated audio file
        """
        try:
            # Create a gTTS object
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            
            # If no output file is specified, create a temporary file
            if output_file is None:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    output_file = tmp_file.name
            
            # Save the audio file
            tts.save(output_file)
            logger.info(f"Audio saved to {output_file}")
            
            return output_file
        
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return None
    
    def speak(self, text, output_file=None):
        """
        Convert text to speech and play it
        
        Args:
            text: The text to speak
            output_file: The path to save the audio file (if None, a temporary file is used)
            
        Returns:
            The path to the generated audio file
        """
        # Convert text to speech
        audio_file = self.text_to_speech(text, output_file)
        
        if audio_file:
            try:
                # Load the audio file
                audio = AudioSegment.from_mp3(audio_file)
                
                # Play the audio
                play(audio)
                
                # If a temporary file was created, remove it
                if output_file is None:
                    os.remove(audio_file)
                
                return audio_file
            
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
                return audio_file
        
        return None


# For testing
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak("Hello, I am your voice assistant. How can I help you today?")
