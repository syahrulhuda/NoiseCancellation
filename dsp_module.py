import numpy as np, noisereduce as nr
from scipy.signal import butter, sosfilt

def filter(data, cut, fs, type='low'):
    sos = butter(5, np.array(cut)/(0.5*fs), btype=type, output='sos'); return sosfilt(sos, data)

def process_noise_cancellation(y, sr, lvl):
    if lvl <= 0: return y, np.zeros_like(y)
    clean = nr.reduce_noise(y=y, sr=sr, prop_decrease=lvl, stationary=True)
    return clean, y - clean

def process_echo_cancellation(y, lvl):
    return y if lvl <= 0 else np.where(np.abs(y) > (0.001 + lvl*0.05), y, 0)

def process_studio_effect(y, sr, lvl):
    if lvl <= 0: return y
    bass, treble = filter(y, 150, sr, 'low'), filter(y, 5000, sr, 'high')
    mixed = (bass + treble) * (1 + lvl*2) + (y - (bass + treble))
    return mixed / (np.max(np.abs(mixed)) + 1e-9)