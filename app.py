import streamlit as st
import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io
from dsp_module import reduce_noise, simple_equalizer, apply_echo

st.set_page_config(page_title="Audio Enhancer", layout="wide")

st.title("🎛️ Audio Post-Processing Workbench")
st.markdown("Proyek Akhir PSD | **Noise Cancellation & Equalizer**")
st.divider()

# --- SIDEBAR KONTROL ---
st.sidebar.header("🎚️ Control Panel")

# 1. Noise Cancellation
st.sidebar.subheader("1. Noise Reduction")
enable_nc = st.sidebar.checkbox("Aktifkan Noise Cancellation", value=False)

# 2. Equalizer
st.sidebar.subheader("2. Equalizer")
gain_low = st.sidebar.slider("Bass (Low)", 0.0, 2.0, 1.0, 0.1)
gain_mid = st.sidebar.slider("Vocal (Mid)", 0.0, 2.0, 1.0, 0.1)
gain_high = st.sidebar.slider("Treble (High)", 0.0, 2.0, 1.0, 0.1)

# 3. Efek
st.sidebar.subheader("3. Efek Audio")
enable_echo = st.sidebar.checkbox("Aktifkan Echo (Delay)", value=False)

# --- AREA UTAMA ---
col1, col2 = st.columns(2)

uploaded_file = st.file_uploader("Upload File Audio (.wav)", type=["wav"])

if uploaded_file is not None:
    # Load Audio
    # y = data sinyal (array), sr = sample rate
    y, sr = librosa.load(uploaded_file, sr=None)
    
    # --- KOLOM KIRI: INPUT ---
    with col1:
        st.subheader("Original Audio")
        st.audio(uploaded_file, format='audio/wav')
        
        # Plot Sinyal Asli
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(np.linspace(0, len(y)/sr, len(y)), y, alpha=0.7)
        ax.set_title("Time Domain - Original")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)

    # --- PROSES DSP ---
    processed_audio = y.copy()
    
    # 1. Noise Cancel
    if enable_nc:
        with st.spinner('Menghilangkan Noise...'):
            processed_audio = reduce_noise(processed_audio, sr)
            
    # 2. Equalizer
    processed_audio = simple_equalizer(processed_audio, sr, gain_low, gain_mid, gain_high)
    
    # 3. Echo
    if enable_echo:
        processed_audio = apply_echo(processed_audio, sr)

    # --- KOLOM KANAN: OUTPUT ---
    with col2:
        st.subheader("Processed Audio")
        
        # Simpan ke buffer memory agar bisa diputar
        virtual_file = io.BytesIO()
        sf.write(virtual_file, processed_audio, sr, format='WAV')
        st.audio(virtual_file, format='audio/wav')
        
        # Plot Sinyal Hasil
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        ax2.plot(np.linspace(0, len(processed_audio)/sr, len(processed_audio)), processed_audio, color='green', alpha=0.7)
        ax2.set_title("Time Domain - Processed")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Amplitude")
        st.pyplot(fig2)