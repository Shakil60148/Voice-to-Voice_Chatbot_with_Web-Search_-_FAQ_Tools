import os
import requests
from dotenv import load_dotenv
import argparse
import json
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
    print(f"Uploading file: {audio_file_path}")
    
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
            upload_url = response.json()["upload_url"]
            print(f"File uploaded successfully. URL: {upload_url}")
            return upload_url
        else:
            print(f"Upload failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error during file upload: {e}")
        return None

def transcribe_audio(audio_file_path, output_file=None):
    """
    Transcribe an audio file using AssemblyAI
    
    Args:
        audio_file_path (str): Path to the audio file
        output_file (str, optional): Path to save the transcription text
        
    Returns:
        str: Transcription text
    """
    print(f"Starting transcription for file: {audio_file_path}")
    
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
            
            print(f"Transcription started with ID: {transcript_id}")
            print("Waiting for transcription to complete...")
            
            # Poll for the transcription to complete
            while True:
                transcription_result = requests.get(polling_endpoint, headers=headers).json()
                
                status = transcription_result["status"]
                
                if status == "completed":
                    print("Transcription completed successfully!")
                    transcription_text = transcription_result["text"]
                    
                    # Save to file if requested
                    if output_file:
                        with open(output_file, "w") as f:
                            f.write(transcription_text)
                        print(f"Transcription saved to: {output_file}")
                    
                    return transcription_text
                elif status == "error":
                    print(f"Transcription failed: {transcription_result.get('error', 'Unknown error')}")
                    return None
                else:
                    # Print progress if available
                    if "percent" in transcription_result:
                        print(f"Progress: {transcription_result['percent']}%")
                
                # Wait a bit before polling again
                time.sleep(3)
        else:
            print(f"Transcription request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using AssemblyAI")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("-o", "--output", help="Path to save the transcription text")
    
    args = parser.parse_args()
    
    # Check if the API key is set
    if not API_KEY:
        print("AssemblyAI API key not found. Please set the ASSEMBLYAI_API_KEY environment variable.")
        return
    
    # Check if the file exists
    if not os.path.exists(args.audio_file):
        print(f"File not found: {args.audio_file}")
        return
    
    # Transcribe the audio
    transcription = transcribe_audio(args.audio_file, args.output)
    
    if transcription:
        print("\nTranscription:")
        print("-" * 80)
        print(transcription)
        print("-" * 80)

if __name__ == "__main__":
    main()
