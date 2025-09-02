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
            print(f"Upload failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error during file upload: {e}")
        return None

def transcribe_audio(audio_file_path, show_progress=True):
    """
    Transcribe an audio file using AssemblyAI
    
    Args:
        audio_file_path (str): Path to the audio file
        show_progress (bool): Whether to show progress indicators (for Streamlit UI)
        
    Returns:
        str: Transcription text
    """
    # First, upload the file
    if show_progress:
        with st.spinner("Uploading audio file..."):
            upload_url = upload_file(audio_file_path)
    else:
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
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            dots = 0
            while True:
                transcription_result = requests.get(polling_endpoint, headers=headers).json()
                
                if transcription_result["status"] == "completed":
                    if show_progress:
                        progress_bar.progress(100)
                        status_text.write("Transcription completed!")
                    return transcription_result["text"]
                elif transcription_result["status"] == "error":
                    error_msg = f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
                    if show_progress:
                        st.error(error_msg)
                    else:
                        print(error_msg)
                    return None
                
                # Update progress
                if show_progress:
                    # Display a simple animation to show that processing is ongoing
                    dots = (dots % 3) + 1
                    status = f"Transcribing{'.' * dots}{' ' * (3 - dots)}"
                    status_text.write(status)
                    
                    # Update progress if available
                    if "percent" in transcription_result:
                        progress = transcription_result["percent"]
                        progress_bar.progress(progress)
                
                # Wait a bit before polling again
                time.sleep(2)
        else:
            error_msg = f"Transcription request failed with status code {response.status_code}: {response.text}"
            if show_progress:
                st.error(error_msg)
            else:
                print(error_msg)
            return None
    except Exception as e:
        error_msg = f"Error during transcription: {e}"
        if show_progress:
            st.error(error_msg)
        else:
            print(error_msg)
        return None
