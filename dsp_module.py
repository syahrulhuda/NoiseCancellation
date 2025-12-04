import numpy as np
import noisereduce as nr
from scipy.signal import butter, sosfilt

def butter_filter(data, cutoff, fs, btype='low', order=5):
    # Menggunakan output='sos' lebih stabil daripada b, a
    nyq = 0.5 * fs
    normal_cutoff = [c / nyq for c in cutoff] if isinstance(cutoff, list) else cutoff / nyq
    sos = butter(order, normal_cutoff, btype=btype, analog=False, output='sos')
    return sosfilt(sos, data)

def process_noise_cancellation(audio, sr, level):
    if level <= 0: return audio, np.zeros_like(audio)
    # Stationary=True lebih cepat untuk noise konstan (kipas/AC)
    reduced = nr.reduce_noise(y=audio, sr=sr, prop_decrease=level, stationary=True)
    return reduced, audio - reduced

def process_echo_cancellation(audio, level):
    if level <= 0: return audio
    threshold = 0.001 + (level * 0.05)
    # One-liner menggunakan numpy masking, jauh lebih efisien
    return np.where(np.abs(audio) > threshold, audio, 0)

def process_studio_effect(audio, sr, level):
    if level <= 0: return audio
    
    # Satu baris pemanggilan filter
    bass = butter_filter(audio, 150, sr, 'low')
    treble = butter_filter(audio, 5000, sr, 'high')
    mids = audio - (bass + treble) # Trik: Mids adalah sisa sinyal tanpa bass & treble
    
    factor = 1.0 + (level * 2.0)
    mixed = (bass * factor) + mids + (treble * factor)
    
    # Normalisasi aman (hindari bagi 0)
    return mixed / (np.max(np.abs(mixed)) + 1e-9)