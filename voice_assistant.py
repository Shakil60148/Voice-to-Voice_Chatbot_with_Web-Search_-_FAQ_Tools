import os
import streamlit as st
import tempfile
from dotenv import load_dotenv

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Voice Assistant with Web Search",
    page_icon="🎤",
    layout="wide"
)

# Import our modules
from answer_agent import AnswerAgent
from text_to_speech import TextToSpeech
from audio_processing import transcribe_audio

# Load environment variables
load_dotenv()

# Initialize the answer agent and text-to-speech engine
@st.cache_resource
def load_answer_agent():
    return AnswerAgent()

@st.cache_resource
def load_tts_engine():
    return TextToSpeech()

# Function to process the audio and get an answer
def process_audio_and_answer(audio_file_path):
    # Transcribe the audio
    with st.spinner("Transcribing your question..."):
        transcription = transcribe_audio(audio_file_path, show_progress=True)
        
        if not transcription:
            st.error("Failed to transcribe the audio. Please try again.")
            return None, None
    
    # Display the transcription
    st.success("Transcription complete!")
    st.subheader("Your Question:")
    st.write(transcription)
    
    # Get the answer
    with st.spinner("Finding an answer..."):
        answer_agent = load_answer_agent()
        response = answer_agent.get_answer(transcription)
    
    return transcription, response

# Main function
def main():
    st.title("🎤 Voice Assistant with Web Search & FAQ")
    st.write("Ask a question by voice and get an answer from our knowledge base or the web.")
    
    # Check for API keys
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        st.warning("AssemblyAI API key not found. Please add it to the .env file.")
    
    if not os.getenv("TAVILY_API_KEY"):
        st.warning("Tavily API key not found. Web search will not be available.")
    
    # Create sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This voice assistant can:
        1. Convert your speech to text
        2. Answer common questions from a local database
        3. Search the web for information using Tavily
        4. Convert the answer back to speech
        """)
        
        st.header("FAQ Database")
        st.markdown("""
        The assistant knows about:
        - Voice assistants
        - Speech recognition
        - AI and machine learning
        - Privacy concerns
        - And more!
        """)
    
    # File uploader for audio
    uploaded_file = st.file_uploader("Upload an audio file with your question", type=["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"])
    
    # Audio recorder (alternative to file upload)
    st.write("Or record your question directly:")
    
    # We can't directly use st.audio with microphone recording, so we'll instruct the user
    st.info("Click the 'Record' button below, speak your question, then click 'Stop' when done.")
    
    # Create columns for the audio controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        record_button = st.button("🎙️ Record")
    
    with col2:
        stop_button = st.button("⏹️ Stop")
    
    # Placeholder for recording status
    recording_status = st.empty()
    
    # Logic for recording (simplified - in a real app, you'd use JavaScript to handle this)
    if record_button:
        recording_status.info("Recording... Speak your question now.")
    
    if stop_button:
        recording_status.success("Recording stopped. Processing...")
        # In a real implementation, this would save the recording
        # For now, we'll just instruct the user to upload a file
        recording_status.info("Please upload your recorded file above.")
    
    # Process uploaded file
    if uploaded_file is not None:
        # Display and play the audio
        st.audio(uploaded_file, format="audio/wav")
        
        # Create a button to start processing
        if st.button("Process Question"):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                # Write the uploaded file to the temporary file
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Process the audio and get an answer
            transcription, response = process_audio_and_answer(tmp_file_path)
            
            # Remove the temporary file
            os.unlink(tmp_file_path)
            
            if response:
                # Display the answer
                st.subheader("Answer:")
                
                # Show the source of the answer
                source_emoji = "📚" if response["source"] == "database" else "🌐"
                st.write(f"{source_emoji} Source: {'Local Knowledge Base' if response['source'] == 'database' else 'Web Search'}")
                
                # Display the answer
                st.markdown(response["answer"])
                
                # Convert answer to speech
                with st.spinner("Converting answer to speech..."):
                    tts = load_tts_engine()
                    # Limit text length for TTS to avoid errors
                    text_for_speech = response["answer"][:1000]  # Limit to 1000 chars
                    speech_file = tts.text_to_speech(text_for_speech)
                
                if speech_file:
                    st.subheader("Voice Answer:")
                    with open(speech_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Offer download
                    st.download_button(
                        label="Download Answer Audio",
                        data=audio_bytes,
                        file_name="answer.mp3",
                        mime="audio/mp3"
                    )

if __name__ == "__main__":
    main()
