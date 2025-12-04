import numpy as np
import noisereduce as nr
from scipy.signal import butter, sosfilt

def bandpass_filter(data, low_cut, high_cut, fs, order=5):
    sos = butter(order, [max(1, low_cut)/(fs/2), min(fs/2-1, high_cut)/(fs/2)], btype='band', output='sos')
    return sosfilt(sos, data)

def process_advanced_nc(audio, sr, low_cut, strength, sensitivity):
    # 1. Frequency Isolation: Focus on human voice range (Low Cut to 10kHz)
    audio = bandpass_filter(audio, low_cut, 10000, sr)

    if strength <= 0: return audio, np.zeros_like(audio)

    # 2. Spectral Gating: Reduce noise with time-smoothing to prevent artifacts
    clean = nr.reduce_noise(
        y=audio, sr=sr,
        prop_decrease=min(strength, 0.95), # Cap at 95% to avoid "underwater" sound
        stationary=True,
        n_std_thresh_stationary=1.0 + (sensitivity * 1.0), # Threshold range: 1.0 - 2.0 std
        time_constant_s=2.0,  # 2s smoothing window (prevents crackling)
        n_fft=2048,
        use_tqdm=False
    )

    # 3. Presence Recovery: Boost 2kHz-5kHz range to restore clarity lost during denoising
    presence = bandpass_filter(clean, 2000, 5000, sr)
    final_audio = clean + (presence * 0.2) 

    return final_audio, audio - final_audio