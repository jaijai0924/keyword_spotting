"""
File used to process .wav files in GCS storage and does the following:
- Transforms to melspectrogram image
- Uses in-memory image buffer to not have to store data into disk
- Uploads each image to GCS target storage 
- Preserves folder structure

Author: JaiJai Macabangon, Sayyed Jilani
Email: jaijaimacabangon@gmail.com 
Created: February 16, 2025
"""


# Import Libraries
import os
import pandas as pd
import numpy as np
import librosa
import librosa.display
from google.cloud import storage
import io

from matplotlib import pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

from IPython.display import display, Image

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Google Cloud Storage bucket names
SOURCE_BUCKET = "pmf-data-store"
DESTINATION_BUCKET = "pmf-wav-to-spec"
PMF_GCS_ID = "tactile-talon-448916-p0"
# Initialize Google Cloud Storage client
storage_client = storage.Client(PMF_GCS_ID)

def read_wav_from_gcs(blob) -> io.BytesIO:
    """
    Reads a .wav file from GCS into memory without saving to disk.
    
    Args:
        blob: GCS blob storage
    
    returns:
        wav_buffer
    """
    audio_data = blob.download_as_bytes()  # Read file as bytes
    wav_buffer = io.BytesIO(audio_data)  # Convert bytes to an in-memory file-like object
    print(f"Loaded {blob.name} into memory.")
    return wav_buffer

def save_mel_spectrogram(audio_vector: np.ndarray, sr: int) -> io.BytesIO:
    """
    Generates a 224x224 Mel spectrogram and returns it as an image buffer.

    Args:
        audio_vector (np.ndarray): The input audio signal.
        sr: sample rate 

    returns:
        image_buffer (io.BytesIO): in-memory buffer for a mel spectrogram image as a PNG.
    
    """
    fig_size = 224 / 100  # inches (224 pixels / 100 DPI)
    dpi = 100  # Dots per inch

    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove padding

    sgram = librosa.stft(audio_vector)
    sgram_mag, _ = librosa.magphase(sgram)
    mel_scale_sgram = librosa.feature.melspectrogram(S=sgram_mag, sr=sr)
    mel_sgram = librosa.amplitude_to_db(mel_scale_sgram, ref=np.min)

    librosa.display.specshow(mel_sgram, sr=sr, ax=ax)

    # Save to a BytesIO buffer instead of disk
    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()

    image_buffer.seek(0)  # Reset buffer position

    return image_buffer  # Return image as a buffer

def upload_spectrogram_to_gcs(bucket_name: str, image_buffer: io.BytesIO, destination_blob_name: str) -> None:
    """
    Uploads generated spectrogram image to Google Cloud Storage, keeping folder structure.

    Args:
        bucket_name (str): bucket name in GCS
        image_buffer (io.BytesIO): png image of spectogram in memory
        destination_blob_name (str): blob name target 


    returns:
        None
    """
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload from memory
    blob.upload_from_file(image_buffer, content_type="image/png")

    print(f"Uploaded spectrogram to gs://{bucket_name}/{destination_blob_name}")

def process_wav_file(blob) -> None:
    """
    Reads .wav from GCS, generates a spectrogram, and uploads it while maintaining folder structure.

    Args:
        blob

    returns:
        None
    """
    # Read the .wav file into memory
    wav_buffer = read_wav_from_gcs(blob)

    # Load the audio into librosa with fixed sample rate of 16kHz
    y, sr = librosa.load(wav_buffer, sr=16000)

    # Generate spectrogram
    spectrogram_buffer = save_mel_spectrogram(y, sr)

    # Preserve full folder structure
    destination_blob_name = f"spectrograms/{blob.name.replace('.wav', '.png')}"

    # # Display the generated spectrogram inside the Jupyter Notebook
    # display(Image(data=spectrogram_buffer.getvalue()))

    # Upload spectrogram to GCS
    upload_spectrogram_to_gcs(DESTINATION_BUCKET, spectrogram_buffer, destination_blob_name)

def process_wav_files():
    """Processes all .wav files from GCS, generates spectrograms, and uploads them while keeping full folder structure."""
    source_bucket = storage_client.bucket(SOURCE_BUCKET)
    blobs = source_bucket.list_blobs()

    for blob in blobs:
        if blob.name.endswith(".wav"):
            print(f"Processing {blob.name}...")
            process_wav_file(blob)



if __name__ == "__main__":
    process_wav_files()