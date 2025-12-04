import numpy as np
import noisereduce as nr
from scipy.signal import butter, sosfilt

def bandpass_filter(data, low_cut, high_cut, fs, order=5):
    sos = butter(order, [max(1, low_cut)/(fs/2), min(fs/2-1, high_cut)/(fs/2)], btype='band', output='sos')
    return sosfilt(sos, data)

def process_advanced_nc(audio, sr, low_cut, strength, sensitivity):
    # 1. FREQUENCY CONTROL: Batasi area kerja
    # Suara kipas ada di bawah, suara kresek digital ada di frekuensi sangat tinggi.
    # Kita persempit area fokus suara manusia (Low Cut s.d. 10kHz)
    audio = bandpass_filter(audio, low_cut, 10000, sr)

    if strength <= 0: return audio, np.zeros_like(audio)

    # 2. SPECTRAL GATING (Soft & Smooth)
    # Perbaikan: Mengurangi agresivitas threshold (max 2.0 std) agar suara nafas tidak dianggap noise.
    # time_constant_s: Fitur PENTING untuk smoothing. Ini mencegah bunyi 'kresek' transisi.
    # prop_decrease: Kita limit max 0.95 (sisakan 5% noise) agar suara tidak terdengar "bolong/underwater".
    
    clean = nr.reduce_noise(
        y=audio, sr=sr,
        prop_decrease=min(strength, 0.95), # Jangan pernah 100% (bikin artifak)
        stationary=True,
        n_std_thresh_stationary=1.0 + (sensitivity * 1.0), # Range lebih aman (1.0 - 2.0)
        time_constant_s=2.0,  # Smoothing waktu (rata-rata 2 detik) -> ILANGIN KRESEK
        n_fft=2048,
        use_tqdm=False
    )

    # 3. PRESENCE RECOVERY (Pengganti Gate Kasar)
    # Daripada memotong (gate), kita justru mengangkat sedikit frekuensi vokal (2kHz-5kHz)
    # agar suara yang "mendem" karena noise reduction jadi jelas lagi.
    presence = bandpass_filter(clean, 2000, 5000, sr)
    final_audio = clean + (presence * 0.2) # Tambah 20% clarity

    return final_audio, audio - final_audio