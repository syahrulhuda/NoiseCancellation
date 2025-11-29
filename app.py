import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import os
import threading

# Import rumus dari file sebelah
from dsp_module import reduce_noise, simple_equalizer, apply_echo

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyek PSD: Audio Enhancer (Desktop GUI)")
        self.root.geometry("1000x700")

        # Variabel global untuk data audio
        self.y = None
        self.sr = None
        self.processed_audio = None
        self.file_path = None

        # --- LAYOUT KIRI (KONTROL) ---
        control_frame = tk.Frame(root, width=300, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="Control Panel", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        # Tombol Upload
        tk.Button(control_frame, text="📂 Buka File (.wav)", command=self.load_file, bg="white", height=2).pack(fill=tk.X, pady=5)
        self.lbl_filename = tk.Label(control_frame, text="File: Belum ada", bg="#f0f0f0", wraplength=200)
        self.lbl_filename.pack(pady=5)

        tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)

        # 1. Noise Cancellation
        self.var_nc = tk.BooleanVar()
        tk.Checkbutton(control_frame, text="Aktifkan Noise Cancellation", variable=self.var_nc, bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w")

        tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)

        # 2. Equalizer Sliders
        tk.Label(control_frame, text="Equalizer", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        tk.Label(control_frame, text="Bass (Low)", bg="#f0f0f0").pack(anchor="w")
        self.scale_low = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.scale_low.set(1.0)
        self.scale_low.pack(fill=tk.X)

        tk.Label(control_frame, text="Vocal (Mid)", bg="#f0f0f0").pack(anchor="w")
        self.scale_mid = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.scale_mid.set(1.0)
        self.scale_mid.pack(fill=tk.X)

        tk.Label(control_frame, text="Treble (High)", bg="#f0f0f0").pack(anchor="w")
        self.scale_high = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.scale_high.set(1.0)
        self.scale_high.pack(fill=tk.X)

        tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)

        # 3. Echo Effect
        self.var_echo = tk.BooleanVar()
        tk.Checkbutton(control_frame, text="Aktifkan Echo (Delay)", variable=self.var_echo, bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w")

        tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=20)

        # Tombol Proses & Play
        tk.Button(control_frame, text="⚙️ PROSES AUDIO", command=self.process_audio, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, pady=5)
        
        tk.Button(control_frame, text="▶️ Play Hasil (System Player)", command=self.play_audio, bg="#2196F3", fg="white", height=2).pack(fill=tk.X, pady=5)

        # --- LAYOUT KANAN (GRAFIK) ---
        graph_frame = tk.Frame(root, bg="white")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Siapkan tempat untuk plot Matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 5))
        self.fig.tight_layout(pad=4.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.reset_plots()

    def reset_plots(self):
        self.ax1.clear()
        self.ax1.set_title("Original Audio Signal")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.grid(True, alpha=0.3)

        self.ax2.clear()
        self.ax2.set_title("Processed Audio Signal")
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.grid(True, alpha=0.3)
        
        self.canvas.draw()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.file_path = file_path
            self.lbl_filename.config(text=f"File: {os.path.basename(file_path)}")
            
            # Load audio dengan librosa
            self.y, self.sr = librosa.load(file_path, sr=None)
            
            # Plot sinyal asli
            self.ax1.clear()
            time_axis = np.linspace(0, len(self.y) / self.sr, num=len(self.y))
            self.ax1.plot(time_axis, self.y, color='blue', alpha=0.6)
            self.ax1.set_title("Original Audio Signal")
            self.ax1.grid(True, alpha=0.3)
            self.canvas.draw()

    def process_audio(self):
        if self.y is None:
            messagebox.showwarning("Peringatan", "Upload file audio dulu!")
            return

        # Ambil nilai dari slider/checkbox
        use_nc = self.var_nc.get()
        use_echo = self.var_echo.get()
        g_low = self.scale_low.get()
        g_mid = self.scale_mid.get()
        g_high = self.scale_high.get()

        # Proses di thread terpisah biar GUI gak macet
        # (Simpelnya kita jalankan langsung aja untuk tugas kuliah)
        processed = self.y.copy()

        # 1. Noise Cancellation
        if use_nc:
            print("Processing: Noise Cancellation...")
            processed = reduce_noise(processed, self.sr)

        # 2. Equalizer
        print("Processing: Equalizer...")
        processed = simple_equalizer(processed, self.sr, g_low, g_mid, g_high)

        # 3. Echo
        if use_echo:
            print("Processing: Echo...")
            processed = apply_echo(processed, self.sr)

        self.processed_audio = processed
        
        # Plot sinyal hasil
        self.ax2.clear()
        time_axis = np.linspace(0, len(processed) / self.sr, num=len(processed))
        self.ax2.plot(time_axis, processed, color='green', alpha=0.6)
        self.ax2.set_title("Processed Audio Signal")
        self.ax2.grid(True, alpha=0.3)
        self.canvas.draw()
        
        messagebox.showinfo("Sukses", "Audio berhasil diolah!")

    def play_audio(self):
        if self.processed_audio is None:
            messagebox.showwarning("Peringatan", "Proses audio dulu sebelum diputar!")
            return
            
        # Simpan ke file sementara lalu buka pakai player bawaan Windows
        output_filename = "hasil_output.wav"
        sf.write(output_filename, self.processed_audio, self.sr)
        
        # Buka file di player default sistem (Windows Media Player / Groove)
        if os.name == 'nt': # Windows
            os.startfile(output_filename)
        else: # Mac/Linux
            os.system(f"open {output_filename}" if os.name == 'posix' else f"xdg-open {output_filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)
    root.mainloop()