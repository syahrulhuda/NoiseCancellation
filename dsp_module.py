import numpy as np
from scipy.signal import butter, lfilter
import noisereduce as nr

# --- 1. FITUR NOISE CANCELLATION ---
def reduce_noise(y, sr):
    # Menggunakan teknik spectral gating
    # y = data audio, sr = sample rate
    # prop_decrease = seberapa agresif noise dikurangi (0.0 sampai 1.0)
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.75) 
    return reduced_noise

# --- 2. FITUR FILTER (LPF, HPF, BPF) ---
def butter_filter(data, cutoff, fs, order=5, btype='low'):
    nyq = 0.5 * fs # Frekuensi Nyquist
    
    # Normalisasi frekuensi cutoff
    if isinstance(cutoff, list):
        normal_cutoff = [c / nyq for c in cutoff]
    else:
        normal_cutoff = cutoff / nyq
        
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    y = lfilter(b, a, data)
    return y

# --- 3. FITUR EQUALIZER (Gabungan Filter) ---
def simple_equalizer(data, fs, gain_low, gain_mid, gain_high):
    # Bass: LPF di bawah 250Hz
    bass = butter_filter(data, 250, fs, btype='low') * gain_low
    
    # Mid: BPF antara 250Hz - 4000Hz
    mid = butter_filter(data, [250, 4000], fs, btype='band') * gain_mid
    
    # Treble: HPF di atas 4000Hz
    treble = butter_filter(data, 4000, fs, btype='high') * gain_high
    
    return bass + mid + treble

# --- 4. FITUR EFEK (ECHO/DELAY) ---
def apply_echo(data, sr, delay_seconds=0.2, decay=0.5):
    # Hitung jumlah sampel delay
    delay_samples = int(sr * delay_seconds)
    
    # Buat array output yang lebih panjang untuk menampung gema
    output_audio = np.zeros(len(data) + delay_samples)
    
    # Sinyal asli
    output_audio[:len(data)] += data
    
    # Sinyal gema (digeser dan dikecilkan volumenya)
    output_audio[delay_samples:] += data * decay
    
    # Kembalikan dengan panjang yang sama seperti asli (opsional)
    return output_audio[:len(data)]