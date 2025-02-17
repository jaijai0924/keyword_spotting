import subprocess
import smtplib
import sys

from ultralytics import YOLO
import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import librosa
from PIL import Image
import io
import cv2
from IPython.display import display
import time
from glob import glob
import random
import datetime

fan_model = YOLO('/Users/sayyedjilani/datasci210/full_models/runs/classify/train/weights/last.pt')
pump_model = YOLO('/Users/sayyedjilani/datasci210/full_models/runs/classify/train2/weights/last.pt')
slider_model = YOLO('/Users/sayyedjilani/datasci210/full_models/runs/classify/train3/weights/last.pt')
valve_model = YOLO('/Users/sayyedjilani/datasci210/full_models/runs/classify/train4/weights/last.pt')

def predict_from_audio(audio_path, model):
    
    # Load the .wav file
    audio_vector, sr = librosa.load(audio_path, sr=None)
    
    # Set the figure size and DPI to get a 224x224 image
    fig_size = 224 / 100  # inches (224 pixels / 100 DPI)
    dpi = 100  # Dots per inch

    # Plot and save Mel spectrogram as an image
    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove padding
    
    sgram = librosa.stft(audio_vector)  # Extract short time fourier transform
    sgram_mag, _ = librosa.magphase(sgram)
    mel_scale_sgram = librosa.feature.melspectrogram(S=sgram_mag, sr=sr)
    mel_sgram = librosa.amplitude_to_db(mel_scale_sgram, ref=np.min)  # Decibel scale
    
    librosa.display.specshow(mel_sgram, sr=sr, ax=ax)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()

    # Collect Mel from memory buffer
    buf.seek(0)
    mel_sgram_image = Image.open(buf).convert('RGB')

    
    # Make prediction on Mel
    pred = model(mel_sgram_image,verbose=False)
    pred_class = np.argmax(pred[0].probs.data.numpy())  

    
    # Output string values for the classification
    if pred_class == 0:
        pred_class = 'abnormal'
    else:
        pred_class = 'normal'
    
    return pred_class

def send_imessage(email, message):
    script = """
    on run {targetEmail, targetMessage}
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to buddy targetEmail of targetService
            send targetMessage to targetBuddy
        end tell
    end run
    """

    apple_script = f"""
    osascript -e '{script}' '{email}' '{message}'
    """

    process = subprocess.Popen(apple_script, shell=True, stdout=subprocess.PIPE)
    process.wait()
    result = process.stdout.read()
    return result


fans = glob('/Users/sayyedjilani/datasci210/*_fan/*/normal/*.wav')
random.shuffle(fans)
fans = fans[:10]

# Get the list of abnormal fan audio files and shuffle it
fans_ab = glob('/Users/sayyedjilani/datasci210/*_fan/*/abnormal/*.wav')
random.shuffle(fans_ab)
fans_ab = fans_ab[:3]

fans.extend(fans_ab)
random.shuffle(fans)

# Example usage
email = "jaijaimacabangon@gmail.com"
message = "Hello from Python!"

for fan_audio in fans:
    
    pred = predict_from_audio(fan_audio, fan_model)

    id = fan_audio.split('/')[-3]
    audio = fan_audio.split('/')[-1]

    message = f"""POTENTIAL MECHANICAL FAILURE:
    Machine: FAN
    ID: {id}
    FILE NAME: {audio}
    WHEN: {datetime.datetime.now()}
    
    """

    if pred == 'abnormal':
        send_imessage(email, message)