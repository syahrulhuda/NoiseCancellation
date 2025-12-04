import numpy as np
import noisereduce as nr
from scipy.signal import butter, sosfilt

def bandpass_filter(data, low_cut, high_cut, fs, order=5):
    sos = butter(order, [max(1, low_cut)/(fs/2), min(fs/2-1, high_cut)/(fs/2)], btype='band', output='sos')
    return sosfilt(sos, data)

def process_advanced_nc(audio, sr, low_cut, strength, sensitivity):
    # 1. Frequency Isolation
    audio = bandpass_filter(audio, low_cut, 10000, sr)

    if strength <= 0: return audio, np.zeros_like(audio), 0.0

    # 2. Spectral Gating (Smooth)
    clean = nr.reduce_noise(
        y=audio, sr=sr,
        prop_decrease=min(strength, 0.95),
        stationary=True,
        n_std_thresh_stationary=1.0 + (sensitivity * 1.0),
        time_constant_s=2.0, 
        n_fft=2048, use_tqdm=False
    )

    # 3. Presence Recovery
    presence = bandpass_filter(clean, 2000, 5000, sr)
    final = clean + (presence * 0.2) 
    
    # 4. Calculate Stats (SNR)
    # SNR = 10 * Log10(Power_Signal / Power_Noise)
    noise = audio - final
    p_sig = np.mean(final**2)
    p_noise = np.mean(noise**2)
    snr = 10 * np.log10((p_sig / (p_noise + 1e-9))) # +1e-9 to avoid div by zero

    return final, noise, snr