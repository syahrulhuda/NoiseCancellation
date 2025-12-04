import numpy as np, noisereduce as nr
from scipy.signal import butter, sosfilt

def process_noise_cancellation(y, sr, lvl):
    if lvl <= 0: return y, np.zeros_like(y)
    # 1. Bandpass Filter: Fokus hanya ke frekuensi suara manusia (80Hz - 8kHz)
    # Ini akan INSTAN membuang suara gemuruh kipas (low rumble)
    sos = butter(4, [80/(sr/2), 8000/(sr/2)], btype='band', output='sos')
    y_band = sosfilt(sos, y)
    
    # 2. Spectral Gating: Threshold dibuat SANGAT GALAK (1.5 -> 4.0)
    clean = nr.reduce_noise(y=y_band, sr=sr, prop_decrease=lvl, stationary=True, n_std_thresh_stationary=1.5+(lvl*2.5))
    return clean, y - clean

def process_echo_cancellation(y, lvl):
    # Hard Gate: Potong habis suara kecil (silence total)
    return np.where(np.abs(y) > (0.005 + lvl*0.1), y, 0) if lvl > 0 else y

def process_studio_effect(y, sr, lvl):
    if lvl <= 0: return y
    # Simple EQ: Boost Bass (<200Hz) dan Treble (>3kHz) dari sinyal bersih
    bass = sosfilt(butter(4, 200/(sr/2), btype='low', output='sos'), y)
    treble = sosfilt(butter(4, 3000/(sr/2), btype='high', output='sos'), y)
    mix = y + (bass * lvl * 3.0) + (treble * lvl * 2.0)
    return mix / (np.max(np.abs(mix)) + 1e-9)