import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
import os
from glob import glob
from typing import Dict, Tuple, List


import librosa
import librosa.display
import IPython.display as ipd




class EDAHelper:
    def __init__(self, file_path: str, age):
        # self.name = name
        self.age = age
        self.audio_files = glob(file_path)