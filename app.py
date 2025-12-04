import tkinter as tk, threading, os
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt, numpy as np, soundfile as sf, librosa
import dsp_module as dsp

class AudioApp:
    def __init__(self, root):
        self.root, self.data = root, {"raw": None, "final": None}
        root.title("Audio Workbench Pro"); root.geometry("1100x750")
        
        # --- UI Setup ---
        p_ctrl = tk.Frame(root, width=300, bg="#2c3e50", padx=15, pady=20); p_ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=0)
        tk.Label(p_ctrl, text="🎛️ DSP PRO", font=("Bold", 18), fg="white", bg="#2c3e50").pack(pady=(0,20))
        
        btn_style = {"bg": "#e74c3c", "fg": "white", "font": ("Bold", 10), "relief": tk.FLAT, "pady": 8}
        tk.Button(p_ctrl, text="📂 Import Audio", **btn_style, command=self.load).pack(fill=tk.X)
        self.lbl_info = tk.Label(p_ctrl, text="-", fg="#bdc3c7", bg="#2c3e50"); self.lbl_info.pack(pady=5)

        self.sliders = {}
        for txt, key in [("Noise Reduce", "nc"), ("Echo Gate", "echo"), ("Studio EQ", "studio")]:
            tk.Label(p_ctrl, text=txt, fg="white", bg="#2c3e50", anchor="w").pack(fill=tk.X, pady=(15,0))
            self.sliders[key] = tk.Scale(p_ctrl, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL, bg="#2c3e50", fg="white", highlightthickness=0)
            self.sliders[key].pack(fill=tk.X)

        tk.Button(p_ctrl, text="⚙️ Process", **{**btn_style, "bg": "#27ae60"}, command=lambda: threading.Thread(target=self.process).start()).pack(fill=tk.X, pady=(20, 5))
        tk.Button(p_ctrl, text="▶️ Play", **{**btn_style, "bg": "#2980b9"}, command=self.play).pack(fill=tk.X)

        # --- Plotting ---
        self.fig, self.axs = plt.subplots(4, 1, figsize=(8, 8), sharex=True); self.fig.subplots_adjust(0.05, 0.05, 0.98, 0.95, 0.3)
        self.lines, titles = {}, ["Raw Input", "Denoised", "Noise Profile", "Master Output"]
        for ax, t, c in zip(self.axs, titles, ['#34495e', '#2980b9', '#c0392b', '#27ae60']):
            ax.set_facecolor("#ecf0f1"); ax.spines['top'].set_visible(0); ax.spines['right'].set_visible(0)
            ax.set_title(t, loc='left', fontsize=9, fontweight='bold'); ax.set_yticks([]); ax.set_xticks([])
            self.lines[t], = ax.plot([], [], color=c, lw=1)
        FigureCanvasTkAgg(self.fig, root).get_tk_widget().pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    def load(self):
        f = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if f: self.data["raw"], self.sr = librosa.load(f, sr=None); self.lbl_info['text'] = os.path.basename(f); self.update_plot(True)

    def process(self):
        if self.data["raw"] is None: return
        try:
            v = {k: s.get() for k, s in self.sliders.items()}
            self.data["clean"], self.data["noise"] = dsp.process_noise_cancellation(self.data["raw"], self.sr, v['nc'])
            self.data["final"] = dsp.process_studio_effect(dsp.process_echo_cancellation(self.data["clean"], v['echo']), self.sr, v['studio'])
            self.root.after(0, self.update_plot)
        except Exception as e: messagebox.showerror("Err", str(e))

    def update_plot(self, init=False):
        for i, (k, t) in enumerate(zip(["raw", "clean", "noise", "final"], self.lines.keys())):
            if (d := self.data.get(k)) is not None:
                vis = d[::100]; self.lines[t].set_data(np.arange(len(vis)), vis)
                self.axs[i].set_xlim(0, len(vis)); self.axs[i].set_ylim(vis.min(), vis.max())
        self.fig.canvas.draw()

    def play(self):
        if self.data["final"] is not None:
            sf.write("out.wav", self.data["final"], self.sr)
            os.startfile("out.wav") if os.name == 'nt' else os.system("xdg-open out.wav")

if __name__ == "__main__": app = tk.Tk(); AudioApp(app); app.mainloop()