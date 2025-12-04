# 🎧 Noise Killer Workbench> **Professional Audio Denoising Tool using Spectral Gating & Frequency Isolation.**> *A Python-based Digital Signal Processing (DSP) project for audio enhancement.*



![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

![License](https://img.shields.io/badge/License-MIT-green)

![Status](https://img.shields.io/badge/Status-Active-success)## 📋 Overview**Noise Killer Workbench** is a desktop application designed to restore audio recordings contaminated by stationary noise (such as fans, air conditioners, or wind rumble). Unlike basic noise reducers, this tool allows users to fine-tune Digital Signal Processing (DSP) parameters in real-time, offering a balance between noise suppression and audio fidelity.



Built with **Tkinter** for the GUI and powered by **SciPy**, **NumPy**, and **NoiseReduce** for the backend, this project demonstrates the practical application of filters and spectral analysis in Telecommunications Engineering.



---## ✨ Key Features* **🎛️ Precision Control:**    * **Low Cut Filter (HPF):** Adjustable cutoff (20-400Hz) to surgically remove low-end rumble (fan/wind).    * **Reduction Strength:** Controls the depth of attenuation (0% - 100%).    * **Aggressiveness:** Fine-tunes the spectral gating threshold to distinguish between noise and voice.* **📊 Visual Analysis:**    * Real-time visualization of **Raw Input**, **Clean Result**, and **Removed Noise Profile**.* **📈 Smart Metrics (New!):**    * **SNR Estimator:** Automatically calculates the estimated **Signal-to-Noise Ratio (dB)** improvement.* **⏯️ A/B Comparison:**    * Dedicated **"Play Orig"** and **"Play Clean"** buttons for instant before-after testing.* **🧠 Audio Preservation:**    * Features a **Presence Recovery** system (2kHz-5kHz boost) to prevent the "muffled" sound typical of aggressive denoising.



---## 🛠️ Technical Methodology



The audio processing pipeline follows a strict DSP chain:1.  **Frequency Isolation (Bandpass Filter):**    * *Input:* Raw Audio Signal.    * *Process:* Butterworth Filter (Order 5).    * *Goal:* Removes mechanical rumble (<100Hz) and high-frequency digital hiss (>10kHz) before processing.2.  **Spectral Gating (The "Noise Killer"):**    * *Process:* Short-Time Fourier Transform (STFT) computes the signal spectrogram.    * *Logic:* A dynamic threshold (controlled by the `Aggressiveness` slider) separates noise bins from signal bins.    * *Smoothing:* A **2.0-second time constant** is applied to the noise mask to prevent "crackling" artifacts.3.  **Presence Recovery (Post-Processing):**    * *Process:* A gentle gain boost in the vocal presence range (2kHz - 5kHz).    * *Goal:* Restores clarity and "air" to the vocals.



---## 💻 Installation Guide (Step-by-Step)



Follow these steps to set up the project on your local machine.### 1. Prerequisites* **Python:** Make sure Python (3.8 or newer) is installed. [Download Here](https://www.python.org/downloads/).* **Git:** Make sure Git is installed. [Download Here](https://git-scm.com/downloads).### 2. Clone the Repository

Open your Terminal (macOS/Linux) or Command Prompt/PowerShell (Windows) and run the following commands:```bash

# 1. Navigate to the folder where you want to save the project (e.g., Desktop)

cd Desktop



# 2. Clone this repository (Download the code)

git clone git@github.com:syahrulhuda/NoiseCancellation.git



# 3. Enter the project folder

cd NoiseCancellation

3. Setup Virtual Environment (Recommended)

It is highly recommended to use a virtual environment to avoid conflicts.

For Windows:

Bash



# Create environment

python -m venv venv# Activate environment

.\venv\Scripts\activate

For macOS / Linux:

Bash



# Create environment

python3 -m venv venv# Activate environmentsource venv/bin/activate

4. Install Dependencies

Once the environment is active (you will see (venv) in your terminal), install the required libraries:

Bash



pip install numpy scipy matplotlib librosa soundfile noisereduce

🚀 How to Use

Run the App:

Make sure your terminal is still inside the project folder and the venv is active, then run:

Bash



python app.py

Workflow:

Click 📂 Load Audio File and select a noisy .wav file.

Adjust Sliders:

Low Cut: ~100Hz (for fans).

Strength: ~0.90.

Aggressiveness: ~0.40.

Click ⚡ PROCESS AUDIO.

Wait for the graphs to appear.

Check Results:

Look at the yellow SNR text to see the improvement.

Use the ▶ Orig and ▶ Clean buttons to hear the difference.

📂 Project Structure

Plaintext



NoiseCancellation/

├── app.py              # Main Application (GUI & Plotting)

├── dsp_module.py       # Core Signal Processing Logic

└── README.md           # Documentation

👨‍💻 Author

Syahrul Huda

Telecommunication Engineering Student

Digital Signal Processing (DSP) Final Project

"Signal is King, Noise is the Enemy."