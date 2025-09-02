import os
import streamlit as st
import requests
from dotenv import load_dotenv
import tempfile
import time

# Load environment variables from .env file
load_dotenv()

# Set AssemblyAI API key from environment variables
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

def upload_file(audio_file_path):
    """
    Upload an audio file to AssemblyAI
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: URL of the uploaded file
    """
    headers = {
        "authorization": API_KEY,
        "content-type": "application/json"
    }
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = requests.post(
                UPLOAD_ENDPOINT,
                headers=headers,
                data=audio_file
            )
        
        if response.status_code == 200:
            return response.json()["upload_url"]
        else:
            st.error(f"Upload failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error during file upload: {e}")
        return None

def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file using AssemblyAI
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcription text
    """
    # First, upload the file
    upload_url = upload_file(audio_file_path)
    
    if not upload_url:
        return None
    
    # Then, start the transcription
    headers = {
        "authorization": API_KEY,
        "content-type": "application/json"
    }
    
    transcript_request = {
        "audio_url": upload_url
    }
    
    try:
        response = requests.post(
            TRANSCRIPT_ENDPOINT,
            json=transcript_request,
            headers=headers
        )
        
        if response.status_code == 200:
            transcript_id = response.json()["id"]
            polling_endpoint = f"{TRANSCRIPT_ENDPOINT}/{transcript_id}"
            
            # Poll for the transcription to complete
            while True:
                transcription_result = requests.get(polling_endpoint, headers=headers).json()
                
                if transcription_result["status"] == "completed":
                    return transcription_result["text"]
                elif transcription_result["status"] == "error":
                    st.error(f"Transcription failed: {transcription_result.get('error', 'Unknown error')}")
                    return None
                
                # Wait a bit before polling again
                time.sleep(3)
        else:
            st.error(f"Transcription request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Voice Assistant with Web Search",
    page_icon="🎤",
    layout="wide"
)

# Import required modules
from answer_agent import AnswerAgent
from text_to_speech import TextToSpeech
from audio_processing import transcribe_audio

# Initialize the answer agent and text-to-speech engine
@st.cache_resource
def load_answer_agent():
    return AnswerAgent()

@st.cache_resource
def load_tts_engine():
    return TextToSpeech()

# Set up the main title and description
st.title("🎤 Voice Assistant with Web Search")
st.markdown("""
This application allows you to ask questions by voice and get spoken answers.
You can either upload an audio file or record your question directly.
""")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Audio", "Record Audio"])

# Define a function to process audio and get answers
def process_audio_and_get_answer(audio_file_path):
    # Transcribe the audio
    with st.spinner("Transcribing your question..."):
        transcription = transcribe_audio(audio_file_path)
        
        if not transcription:
            st.error("Failed to transcribe the audio. Please try again.")
            return
    
    # Display the transcription
    st.success("Transcription complete!")
    st.subheader("Your Question:")
    st.write(transcription)
    
    # Get the answer
    with st.spinner("Finding an answer..."):
        answer_agent = load_answer_agent()
        response = answer_agent.get_answer(transcription)
    
    # Display the answer
    st.subheader("Answer:")
    st.write(response)
    
    # Convert the answer to speech
    with st.spinner("Converting answer to speech..."):
        tts_engine = load_tts_engine()
        audio_file = tts_engine.text_to_speech(response)
    
    # Display the audio player
    st.subheader("Listen to the answer:")
    st.audio(audio_file, format="audio/mp3")

# Tab 1: Upload Audio
with tab1:
    st.header("Upload an audio file with your question")
    uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav", "m4a", "ogg"])
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split(".")[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            audio_file_path = tmp_file.name
        
        # Display the audio player for the uploaded file
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        
        # Add a button to process the audio
        if st.button("Process Audio", key="process_upload"):
            process_audio_and_get_answer(audio_file_path)

# Tab 2: Record Audio
with tab2:
    st.header("Record your question")
    st.write("Click the button below to start recording your question.")
    
    audio_bytes = st.audio_recorder(text="Click to record", pause_threshold=3.0)
    
    if audio_bytes:
        # Save the recorded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            audio_file_path = tmp_file.name
        
        # Display the audio player for the recorded file
        st.audio(audio_bytes, format="audio/wav")
        
        # Add a button to process the audio
        if st.button("Process Audio", key="process_record"):
            process_audio_and_get_answer(audio_file_path)

# Add information about the application
st.sidebar.title("About")
st.sidebar.info("""
This voice assistant can:
1. Transcribe your spoken questions
2. Search for answers in its knowledge base
3. Search the web if needed
4. Convert text answers to speech
""")

# Add a section for FAQ
st.sidebar.title("Sample Questions")
st.sidebar.markdown("""
Try asking:
- What is a voice assistant?
- How does speech recognition work?
- What are some popular voice assistants?
- Tell me about recent AI advancements
""")
