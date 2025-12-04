import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import librosa, threading, os

# Import modul DSP yang sudah disederhanakan
import dsp_module as dsp

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PSD Project: Smart Audio Workbench")
        self.root.geometry("1100x700")
        
        # State Data
        self.data = {"raw": None, "clean": None, "noise": None, "final": None}
        self.sr = None

        # --- GUI Layout ---
        # Panel Kiri (Controls)
        p_left = tk.Frame(root, width=300, bg="#2c3e50", padx=10, pady=10)
        p_left.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(p_left, text="🎛️ DSP Controls", font=("Bold", 14), fg="white", bg="#2c3e50").pack(pady=10)
        
        # 1. Widget Generator (Agar kode pendek)
        self.btn_load = self.create_btn(p_left, "📂 Load Audio", self.load_file, "#e74c3c")
        self.lbl_file = tk.Label(p_left, text="-", fg="#bdc3c7", bg="#2c3e50")
        self.lbl_file.pack()

        # Sliders dictionary untuk akses mudah
        self.sliders = {}
        controls = [("Noise Reduction", "nc"), ("Echo Gate", "echo"), ("Studio Warmth", "studio")]
        for label, key in controls:
            tk.Label(p_left, text=label, fg="white", bg="#2c3e50", anchor="w").pack(fill=tk.X, pady=(10,0))
            s = tk.Scale(p_left, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#34495e", fg="white", highlightthickness=0)
            s.pack(fill=tk.X)
            self.sliders[key] = s

        self.create_btn(p_left, "⚙️ Process", self.run_processing, "#27ae60")
        self.create_btn(p_left, "▶️ Play Result", self.play_audio, "#2980b9")

        # --- Plotting Area (Optimized) ---
        p_right = tk.Frame(root, bg="white")
        p_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.axs = plt.subplots(4, 1, sharex=True, figsize=(6, 8))
        self.fig.tight_layout(pad=2.0)
        self.lines = {} # Simpan referensi garis untuk update cepat
        
        titles = ["Raw Input", "Denoised Audio", "Rejected Noise", "Final Output"]
        colors = ['black', '#2980b9', '#c0392b', '#27ae60']
        
        # Setup plot awal (kosong)
        for i, ax in enumerate(self.axs):
            ax.set_facecolor("#ecf0f1")
            ax.set_ylabel(titles[i], fontsize=8, rotation=0, labelpad=40, ha='left')
            ax.set_yticks([])
            # Plot dummy data, simpan objek garisnya
            line, = ax.plot([], [], color=colors[i], lw=0.8)
            self.lines[titles[i]] = line

        self.canvas = FigureCanvasTkAgg(self.fig, master=p_right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_btn(self, parent, text, cmd, color):
        btn = tk.Button(parent, text=text, command=cmd, bg=color, fg="white", font=("Bold", 10), relief=tk.FLAT, pady=5)
        btn.pack(fill=tk.X, pady=5)
        return btn

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if not path: return
        
        self.data["raw"], self.sr = librosa.load(path, sr=None)
        self.lbl_file.config(text=os.path.basename(path))
        
        # Reset data lain
        zeros = np.zeros_like(self.data["raw"])
        self.data.update({"clean": zeros, "noise": zeros, "final": zeros})
        self.update_viz()

    def run_processing(self):
        if self.data["raw"] is None: return
        threading.Thread(target=self._process_logic).start()

    def _process_logic(self):
        # Ambil value slider
        vals = {k: v.get() for k, v in self.sliders.items()}
        
        # Pipeline DSP
        clean, noise = dsp.process_noise_cancellation(self.data["raw"], self.sr, vals['nc'])
        gated = dsp.process_echo_cancellation(clean, vals['echo'])
        final = dsp.process_studio_effect(gated, self.sr, vals['studio'])
        
        # Update Data & GUI
        self.data.update({"clean": clean, "noise": noise, "final": final})
        self.root.after(0, self.update_viz)
        self.root.after(0, lambda: messagebox.showinfo("Info", "Done!"))

    def update_viz(self):
        # Teknik Optimization: Update y-data saja, jangan redraw axis
        mapping = [("Raw Input", "raw"), ("Denoised Audio", "clean"), 
                   ("Rejected Noise", "noise"), ("Final Output", "final")]
        
        for title, key in mapping:
            signal = self.data[key]
            if signal is None: continue
            
            # Downsample visual (plot tiap 100 sampel) biar ringan
            vis_sig = signal[::50] 
            x_axis = np.arange(len(vis_sig))
            
            line = self.lines[title]
            line.set_data(x_axis, vis_sig) # Update garis
            self.axs[mapping.index((title, key))].set_xlim(0, len(vis_sig)) # Sesuaikan lebar
            
        self.canvas.draw()

    def play_audio(self):
        if self.data["final"] is None: return
        sf.write("temp_out.wav", self.data["final"], self.sr)
        
        # Cross-platform open
        if os.name == 'nt': os.startfile("temp_out.wav")
        else: os.system("xdg-open temp_out.wav")

if __name__ == "__main__":
    root = tk.Tk()
    AudioApp(root)
    root.mainloop()