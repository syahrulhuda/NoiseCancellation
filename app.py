import tkinter as tk, threading, os
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt, numpy as np, soundfile as sf, librosa
import dsp_module as dsp

class NoiseKillerApp:
    def __init__(self, r):
        self.r, self.data = r, {"raw": None, "clean": None, "noise": None}
        r.title("Noise Killer Workbench"); r.geometry("1000x750")
        
        # --- UI Control Panel ---
        p = tk.Frame(r, width=280, bg="#2c3e50", padx=15, pady=20); p.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(p, text="NOISE KILLER", font=("Impact", 20), fg="#e74c3c", bg="#2c3e50").pack(pady=(0,20))
        
        btn_st = {"bg": "#34495e", "fg": "white", "font": ("Arial", 10, "bold"), "relief": "flat", "pady": 8}
        tk.Button(p, text="📂 Load Audio File", **btn_st, command=self.load).pack(fill='x')
        self.lbl = tk.Label(p, text="No File Selected", fg="#95a5a6", bg="#2c3e50"); self.lbl.pack(pady=5)

        # Sliders
        self.s = {}
        self.create_slider(p, "1. Low Cut Filter (Hz)", "cut", 20, 400, 100)
        self.create_slider(p, "2. Reduction Strength (%)", "str", 0.0, 1.0, 0.8, res=0.05)
        self.create_slider(p, "3. Aggressiveness", "sens", 0.0, 1.0, 0.5, res=0.05)

        tk.Button(p, text="⚡ Process Audio", **{**btn_st, "bg": "#27ae60"}, command=lambda: threading.Thread(target=self.run).start()).pack(fill='x', pady=(25,5))
        tk.Button(p, text="▶ Play Result", **{**btn_st, "bg": "#2980b9"}, command=self.play).pack(fill='x')

        # --- Plotting Area ---
        self.fig, self.axs = plt.subplots(3, 1, figsize=(6,8), sharex=True)
        self.fig.subplots_adjust(0.06, 0.05, 0.98, 0.95, 0.3)
        self.lines, titles = {}, ["Raw Input", "Clean Result", "Removed Noise"]
        colors = ['#7f8c8d', '#2ecc71', '#e74c3c'] 
        
        for ax, t, c in zip(self.axs, titles, colors):
            ax.set_facecolor("#ecf0f1"); ax.spines['top'].set_visible(0); ax.spines['right'].set_visible(0)
            ax.set_title(t, loc='left', fontsize=9, fontweight='bold', color="#2c3e50")
            ax.set_yticks([]); ax.set_xticks([])
            self.lines[t], = ax.plot([], [], c=c, lw=0.8)
            
        FigureCanvasTkAgg(self.fig, r).get_tk_widget().pack(fill='both', expand=1, padx=15, pady=15)

    def create_slider(self, parent, label, key, min_val, max_val, def_val, res=1):
        tk.Label(parent, text=label, fg="white", bg="#2c3e50", anchor='w', font=("Arial", 9, "bold")).pack(fill='x', pady=(15,0))
        s = tk.Scale(parent, from_=min_val, to=max_val, resolution=res, orient='horizontal', 
                     bg="#2c3e50", fg="white", highlightthickness=0, troughcolor="#34495e", activebackground="#e74c3c")
        s.set(def_val); s.pack(fill='x'); self.s[key] = s

    def load(self):
        f = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if f: 
            self.data["raw"], self.sr = librosa.load(f, sr=None)
            self.lbl['text'] = os.path.basename(f)
            self.update_plot(True)

    def run(self):
        if self.data["raw"] is None: return
        try:
            # Get slider values
            cut = self.s['cut'].get()
            strength = self.s['str'].get()
            sens = self.s['sens'].get()
            
            # Run DSP
            self.data["clean"], self.data["noise"] = dsp.process_advanced_nc(
                self.data["raw"], self.sr, cut, strength, sens
            )
            self.r.after(0, self.update_plot)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_plot(self, init=False):
        for i, (k, t) in enumerate(zip(["raw", "clean", "noise"], self.lines)):
            if (d := self.data.get(k)) is not None:
                v = d[::50] # Visual downsampling
                self.lines[t].set_data(np.arange(len(v)), v)
                self.axs[i].set_xlim(0, len(v)); self.axs[i].set_ylim(v.min(), v.max())
        self.fig.canvas.draw()

    def play(self):
        if self.data["clean"] is not None:
            sf.write("clean_out.wav", self.data["clean"], self.sr)
            os.startfile("clean_out.wav") if os.name == 'nt' else os.system("xdg-open clean_out.wav")

if __name__ == "__main__": app = tk.Tk(); NoiseKillerApp(app); app.mainloop()