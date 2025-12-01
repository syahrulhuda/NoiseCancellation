import numpy as np
from scipy.signal import butter, lfilter
import noisereduce as nr

# --- 1. CORE FILTERS (HIDDEN) ---
def butter_filter(data, cutoff, fs, order=5, btype='low'):
    nyq = 0.5 * fs
    if isinstance(cutoff, list):
        normal_cutoff = [c / nyq for c in cutoff]
    else:
        normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return lfilter(b, a, data)

# --- 2. FITUR UTAMA ---

def process_noise_cancellation(audio, sr, level):
    """
    level: 0.0 sampai 1.0 (dari slider)
    Mengembalikan: (audio_bersih, audio_noise_saja)
    """
    if level <= 0:
        return audio, np.zeros_like(audio)
    
    # Prop_decrease diatur oleh slider (makin kanan makin hilang noisenya)
    reduced_audio = nr.reduce_noise(y=audio, sr=sr, prop_decrease=level, stationary=True)
    
    # Noise adalah selisih audio asli dengan audio bersih
    noise_only = audio - reduced_audio
    return reduced_audio, noise_only

def process_echo_cancellation(audio, level):
    """
    Menggunakan teknik Noise Gate sederhana.
    level: 0.0 sampai 1.0.
    Semakin tinggi level, semakin agresif memotong suara pelan (buntut echo).
    """
    if level <= 0:
        return audio
    
    # Ambang batas (Threshold) ditentukan oleh level slider
    # Level max (1.0) = threshold 0.1 (agresif), Level min = threshold kecil
    threshold = 0.001 + (level * 0.05) 
    
    # Buat mask: jika amplitudo < threshold, set ke 0 (hilangkan echo tail)
    mask = (np.abs(audio) > threshold)
    
    # Terapkan mask (Gate)
    # Kita haluskan sedikit transisinya agar tidak 'ceguk-ceguk'
    return audio * mask

def process_studio_effect(audio, sr, level):
    """
    Menggunakan LPF dan HPF untuk membuat efek 'Broadcast' (V-Shape EQ).
    Level mengatur seberapa kuat boost Bass dan Treble.
    """
    if level <= 0:
        return audio
    
    # Isolasi frekuensi (Hidden Filters)
    bass = butter_filter(audio, 150, sr, btype='low')
    treble = butter_filter(audio, 5000, sr, btype='high')
    mids = butter_filter(audio, [150, 5000], sr, btype='band')
    
    # Logic: Boost Bass & Treble sesuai level slider
    boost_factor = 1.0 + (level * 2.0) # Max boost 3x
    
    # Gabungkan kembali: Bass(boost) + Mids(normal) + Treble(boost)
    mixed = (bass * boost_factor) + mids + (treble * boost_factor)
    
    # Normalisasi agar tidak pecah (clipping)
    max_val = np.max(np.abs(mixed))
    if max_val > 1.0:
        mixed = mixed / max_val
        
    return mixed