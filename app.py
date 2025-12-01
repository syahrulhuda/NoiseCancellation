import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import os
import threading

# Import logika baru
from dsp_module import process_noise_cancellation, process_echo_cancellation, process_studio_effect

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PSD Project: Audio Workbench")
        self.root.geometry("1200x800")

        # Variables
        self.y_raw = None # Sinyal Mentah
        self.sr = None
        self.y_processed = None # Sinyal Akhir
        self.y_noise = None # Sinyal Noise Saja
        self.y_clean_only = None # Sinyal Audio Saja (setelah NC, sebelum Efek)

        # --- PANEL KIRI (CONTROLS) ---
        left_panel = tk.Frame(root, width=350, bg="#2c3e50", padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Header
        tk.Label(left_panel, text="🎛️ Control Center", font=("Helvetica", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=(0, 20))

        # Upload Button
        self.btn_load = tk.Button(left_panel, text="📂 1. Load Audio (.wav)", command=self.load_file, 
                                  bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), height=2, relief=tk.FLAT)
        self.btn_load.pack(fill=tk.X, pady=5)
        self.lbl_status = tk.Label(left_panel, text="No file loaded", fg="#bdc3c7", bg="#2c3e50")
        self.lbl_status.pack(pady=5)

        tk.Frame(left_panel, height=2, bg="#34495e").pack(fill=tk.X, pady=15)

        # --- SLIDERS ---
        # 1. Noise Cancellation
        tk.Label(left_panel, text="Noise Cancellation", fg="#3498db", bg="#2c3e50", font=("Arial", 10, "bold")).pack(anchor="w")
        self.slider_nc = tk.Scale(left_panel, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#2c3e50", fg="white", highlightthickness=0)
        self.slider_nc.set(0.75) # Default agak tinggi
        self.slider_nc.pack(fill=tk.X, pady=(0, 15))

        # 2. Echo Cancellation (Gate)
        tk.Label(left_panel, text="Echo Cancellation (Gate)", fg="#2ecc71", bg="#2c3e50", font=("Arial", 10, "bold")).pack(anchor="w")
        self.slider_echo = tk.Scale(left_panel, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#2c3e50", fg="white", highlightthickness=0)
        self.slider_echo.set(0.0)
        self.slider_echo.pack(fill=tk.X, pady=(0, 15))

        # 3. Studio Effect
        tk.Label(left_panel, text="Studio Effect (Warmth + Clarity)", fg="#f1c40f", bg="#2c3e50", font=("Arial", 10, "bold")).pack(anchor="w")
        self.slider_studio = tk.Scale(left_panel, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#2c3e50", fg="white", highlightthickness=0)
        self.slider_studio.set(0.0)
        self.slider_studio.pack(fill=tk.X, pady=(0, 15))

        tk.Frame(left_panel, height=2, bg="#34495e").pack(fill=tk.X, pady=15)

        # Process Button
        self.btn_process = tk.Button(left_panel, text="⚙️ 2. Process Audio", command=self.run_processing, 
                                     bg="#27ae60", fg="white", font=("Arial", 11, "bold"), height=2, relief=tk.FLAT)
        self.btn_process.pack(fill=tk.X, pady=5)

        # Play Button
        self.btn_play = tk.Button(left_panel, text="▶️ 3. Play Result", command=self.play_audio, 
                                  bg="#2980b9", fg="white", font=("Arial", 11, "bold"), height=2, relief=tk.FLAT)
        self.btn_play.pack(fill=tk.X, pady=5)

        # --- PANEL KANAN (GRAFIK) ---
        right_panel = tk.Frame(root, bg="white")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Matplotlib Figure (4 Rows)
        self.fig, self.axs = plt.subplots(4, 1, figsize=(8, 8), sharex=True)
        self.fig.tight_layout(pad=3.0)
        self.fig.subplots_adjust(hspace=0.5) # Jarak antar grafik
        
        # Init Judul Grafik kosong
        titles = ["1. Raw Signal (Input)", "2. Audio Only (Filtered)", "3. Noise Only (Removed)", "4. Final Output (Preview)"]
        colors = ['black', 'blue', 'red', 'green']
        
        for ax, title, col in zip(self.axs, titles, colors):
            ax.set_title(title, fontsize=9, fontweight='bold', loc='left')
            ax.set_facecolor("#ecf0f1")
            ax.grid(True, linestyle='--', alpha=0.6)
            # Hilangkan label y axis biar rapi
            ax.set_yticks([]) 

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.y_raw, self.sr = librosa.load(path, sr=None)
            self.lbl_status.config(text=f"...{os.path.basename(path)}")
            self.update_plot(0, self.y_raw, "black")
            
            # Reset grafik lain
            for i in range(1, 4):
                self.axs[i].clear()
                self.axs[i].grid(True)
            self.canvas.draw()

    def run_processing(self):
        if self.y_raw is None:
            messagebox.showwarning("Ops", "Load file dulu!")
            return
        
        # Jalankan di thread biar GUI gak freeze
        t = threading.Thread(target=self.processing_logic)
        t.start()

    def processing_logic(self):
        # Ambil value slider
        val_nc = self.slider_nc.get()
        val_echo = self.slider_echo.get()
        val_studio = self.slider_studio.get()

        # 1. Noise Cancellation
        # Return: Audio Bersih & Noise-nya
        audio_clean, audio_noise = process_noise_cancellation(self.y_raw, self.sr, val_nc)
        self.y_clean_only = audio_clean
        self.y_noise = audio_noise

        # 2. Echo Cancellation (Gate pada sinyal bersih)
        audio_gated = process_echo_cancellation(audio_clean, val_echo)

        # 3. Studio Effect (EQ pada sinyal gated)
        self.y_processed = process_studio_effect(audio_gated, self.sr, val_studio)

        # Update Grafik di Main Thread
        self.root.after(0, self.update_all_plots)
        self.root.after(0, lambda: messagebox.showinfo("Done", "Processing Complete!"))

    def update_plot(self, index, data, color):
        ax = self.axs[index]
        ax.clear()
        
        titles = ["1. Raw Signal (Input)", "2. Audio Only (Cleaned)", "3. Noise Only (Removed)", "4. Final Output (Preview)"]
        ax.set_title(titles[index], fontsize=9, fontweight='bold', loc='left')
        ax.set_facecolor("#ecf0f1")
        
        # Plot dengan downsampling biar cepat (tiap 100 sampel)
        time = np.linspace(0, len(data)/self.sr, len(data))
        ax.plot(time[::50], data[::50], color=color, lw=0.8)
        
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_yticks([]) # Hilangkan angka axis Y

    def update_all_plots(self):
        self.update_plot(0, self.y_raw, "black")
        self.update_plot(1, self.y_clean_only, "#2980b9") # Biru
        self.update_plot(2, self.y_noise, "#c0392b")      # Merah
        self.update_plot(3, self.y_processed, "#27ae60")  # Hijau
        self.canvas.draw()

    def play_audio(self):
        if self.y_processed is None: return
        out_path = "output_result.wav"
        sf.write(out_path, self.y_processed, self.sr)
        if os.name == 'nt':
            os.startfile(out_path)
        else:
            os.system(f"open {out_path}" if os.name == 'posix' else f"xdg-open {out_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)
    root.mainloop()