import tkinter as tk, threading, os
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt, numpy as np, soundfile as sf, librosa
import dsp_module as dsp

class NoiseKillerApp:
    def __init__(self, r):
        self.r, self.data = r, {"raw": None, "clean": None, "noise": None}
        r.title("Noise Killer Workbench"); r.geometry("1000x750")
        
        # --- UI Panel ---
        p = tk.Frame(r, width=280, bg="#2c3e50", padx=15, pady=20); p.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(p, text="NOISE KILLER", font=("Impact", 20), fg="#e74c3c", bg="#2c3e50").pack(pady=(0,20))
        
        btn_st = {"bg": "#34495e", "fg": "white", "font": ("Arial", 9, "bold"), "relief": "flat", "pady": 6}
        tk.Button(p, text="📂 Load Audio File", **btn_st, command=self.load).pack(fill='x')
        self.lbl_file = tk.Label(p, text="-", fg="#7f8c8d", bg="#2c3e50", font=("Arial", 8)); self.lbl_file.pack(pady=5)

        self.s = {} # Sliders
        self.create_slider(p, "1. Low Cut Filter (Hz)", "cut", 20, 400, 100)
        self.create_slider(p, "2. Reduction Strength (%)", "str", 0.0, 1.0, 0.8, res=0.05)
        self.create_slider(p, "3. Aggressiveness", "sens", 0.0, 1.0, 0.5, res=0.05)

        tk.Button(p, text="⚡ PROCESS AUDIO", **{**btn_st, "bg": "#27ae60"}, command=lambda: threading.Thread(target=self.run).start()).pack(fill='x', pady=(20,5))
        
        # STATS LABEL (New!)
        self.lbl_stats = tk.Label(p, text="SNR: - dB", fg="#f1c40f", bg="#2c3e50", font=("Consolas", 10, "bold")); self.lbl_stats.pack(pady=(0, 15))

        # DUAL PLAY BUTTONS (New!)
        f_play = tk.Frame(p, bg="#2c3e50"); f_play.pack(fill='x')
        tk.Button(f_play, text="▶ Orig", **btn_st, width=8, command=lambda: self.play("raw")).pack(side=tk.LEFT, padx=(0,5))
        tk.Button(f_play, text="▶ Clean", **{**btn_st, "bg": "#2980b9"}, width=15, command=lambda: self.play("clean")).pack(side=tk.LEFT)

        # --- Plotting ---
        self.fig, self.axs = plt.subplots(3, 1, figsize=(6,8), sharex=True)
        self.fig.subplots_adjust(0.06, 0.05, 0.98, 0.95, 0.3)
        self.lines, titles = {}, ["Raw Input", "Clean Result", "Removed Noise"]
        
        for ax, t, c in zip(self.axs, titles, ['#7f8c8d', '#2ecc71', '#e74c3c']):
            ax.set_facecolor("#ecf0f1"); ax.spines['top'].set_visible(0); ax.spines['right'].set_visible(0)
            ax.set_title(t, loc='left', fontsize=9, fontweight='bold', color="#2c3e50")
            ax.set_yticks([]); ax.set_xticks([])
            self.lines[t], = ax.plot([], [], c=c, lw=0.8)
        FigureCanvasTkAgg(self.fig, r).get_tk_widget().pack(fill='both', expand=1, padx=15, pady=15)

    def create_slider(self, p, lbl, k, min_v, max_v, def_v, res=1):
        tk.Label(p, text=lbl, fg="white", bg="#2c3e50", anchor='w', font=("Arial", 9, "bold")).pack(fill='x', pady=(10,0))
        self.s[k] = tk.Scale(p, from_=min_v, to=max_v, resolution=res, orient='horizontal', bg="#2c3e50", fg="white", highlightthickness=0, troughcolor="#34495e", activebackground="#e74c3c"); self.s[k].set(def_v); self.s[k].pack(fill='x')

    def load(self):
        f = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if f: self.data["raw"], self.sr = librosa.load(f, sr=None); self.lbl_file['text'] = os.path.basename(f); self.update_plot(True)

    def run(self):
        if self.data["raw"] is None: return
        try:
            v = {k: s.get() for k, s in self.s.items()}
            # Unpack 3 values now (including SNR)
            self.data["clean"], self.data["noise"], snr = dsp.process_advanced_nc(self.data["raw"], self.sr, v['cut'], v['str'], v['sens'])
            
            # Update Stats Label
            self.lbl_stats.config(text=f"Est. SNR: {snr:.2f} dB")
            self.r.after(0, self.update_plot)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_plot(self, init=False):
        for i, (k, t) in enumerate(zip(["raw", "clean", "noise"], self.lines)):
            if (d := self.data.get(k)) is not None:
                v = d[::50]; self.lines[t].set_data(np.arange(len(v)), v)
                self.axs[i].set_xlim(0, len(v)); self.axs[i].set_ylim(v.min(), v.max())
        self.fig.canvas.draw()

    def play(self, type="clean"):
        if self.data[type] is not None:
            sf.write("temp.wav", self.data[type], self.sr)
            os.startfile("temp.wav") if os.name == 'nt' else os.system("xdg-open temp.wav")

if __name__ == "__main__": app = tk.Tk(); NoiseKillerApp(app); app.mainloop()