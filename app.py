import tkinter as tk, threading, os
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt, numpy as np, soundfile as sf, librosa
import dsp_module as dsp

class AudioApp:
    def __init__(self, r):
        self.r, self.data = r, {"raw": None, "final": None}
        r.title("DSP Ultra"); r.geometry("1000x700")
        
        # --- UI Compact ---
        p = tk.Frame(r, width=280, bg="#222", padx=15, pady=20); p.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(p, text="DSP CORE", font=("Bold", 20), fg="#fff", bg="#222").pack(pady=(0,20))
        
        style = {"bg": "#e74c3c", "fg": "#fff", "font": ("Bold", 10), "relief": "flat", "pady": 6}
        tk.Button(p, text="📂 Load WAV", **style, command=self.load).pack(fill='x')
        self.lbl = tk.Label(p, text="-", fg="#777", bg="#222"); self.lbl.pack(pady=5)
        
        self.s = {} # Sliders
        for k, t in [('nc','NOISE FILTER'), ('echo','NOISE GATE'), ('studio','STUDIO EQ')]:
            tk.Label(p, text=t, fg="#aaa", bg="#222", anchor='w', font=("Bold", 8)).pack(fill='x', pady=(15,0))
            self.s[k] = tk.Scale(p, from_=0, to=1, res=0.05, orient='horizontal', bg="#333", fg="white", highlightthickness=0)
            self.s[k].pack(fill='x')

        tk.Button(p, text="⚡ EXECUTE", **{**style, "bg": "#27ae60"}, command=lambda: threading.Thread(target=self.run).start()).pack(fill='x', pady=(20,5))
        tk.Button(p, text="▶ PLAY", **{**style, "bg": "#2980b9"}, command=self.play).pack(fill='x')

        # --- Plot Compact ---
        self.fig, self.axs = plt.subplots(4, 1, figsize=(6,8), sharex=True)
        self.fig.subplots_adjust(0.05, 0.05, 0.98, 0.95, 0.25)
        self.lines, titles = {}, ["INPUT", "DENOISED", "NOISE", "OUTPUT"]
        for ax, t, c in zip(self.axs, titles, ['#555', '#3498db', '#e74c3c', '#2ecc71']):
            ax.set_facecolor("#ecf0f1"); ax.spines['top'].set_visible(0); ax.spines['right'].set_visible(0)
            ax.set_title(t, loc='left', fontsize=8, fontweight='bold', pad=5); ax.set_yticks([]); ax.set_xticks([])
            self.lines[t], = ax.plot([], [], c=c, lw=0.8)
        FigureCanvasTkAgg(self.fig, r).get_tk_widget().pack(fill='both', expand=1, padx=10, pady=10)

    def load(self):
        f = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if f: self.data["raw"], self.sr = librosa.load(f, sr=None); self.lbl['text'] = os.path.basename(f); self.upd(init=True)

    def run(self):
        if self.data["raw"] is None: return
        try:
            v = {k: s.get() for k, s in self.s.items()}
            self.data["clean"], self.data["noise"] = dsp.process_noise_cancellation(self.data["raw"], self.sr, v['nc'])
            self.data["final"] = dsp.process_studio_effect(dsp.process_echo_cancellation(self.data["clean"], v['echo']), self.sr, v['studio'])
            self.r.after(0, self.upd)
        except Exception as e: messagebox.showerror("Err", str(e))

    def upd(self, init=False):
        for i, (k, t) in enumerate(zip(["raw", "clean", "noise", "final"], self.lines)):
            if (d := self.data.get(k)) is not None:
                v = d[::50]; self.lines[t].set_data(np.arange(len(v)), v)
                self.axs[i].set_xlim(0, len(v)); self.axs[i].set_ylim(v.min(), v.max())
        self.fig.canvas.draw()

    def play(self):
        if self.data["final"] is not None:
            sf.write("out.wav", self.data["final"], self.sr)
            os.startfile("out.wav") if os.name == 'nt' else os.system("xdg-open out.wav")

if __name__ == "__main__": app = tk.Tk(); AudioApp(app); app.mainloop()