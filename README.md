# Accent Classification Using Mel-Frequency Cepstral Coefficients and Support Vector Machine on Raspberry Pi

An edge-deployable Machine Learning system for classifying regional Filipino English accents (**Tagalog**, **Ilocano**, and **Bisaya**) using Mel-Frequency Cepstral Coefficients (MFCCs) and Support Vector Machines (SVM). Developed for the Computer Engineering (CpE) Thesis project and published at **ADMIT 2026**.

---

## 📌 System Architecture

The application provides a unified, standardized audio processing and inference pipeline for both live microphone recording and uploaded WAV files:

```
[ Live Microphone Recording ]  ───►  [ Save Uncompressed WAV ]
                                                │
[ Upload Audio File (.wav)  ]  ─────────────────┴──►  [ Librosa Standardized Load (22.05 kHz) ]
                                                                     │
                                                      [ Energy-Based Silence Trimming & Normalization ]
                                                                     │
                                                      [ Feature Extraction (MFCC + Δ + ΔΔ: 78 Features) ]
                                                                     │
                                                      [ StandardScaler + RBF Kernel SVM Inference ]
                                                                     │
                                                      [ Prediction Display & Confidence Scores ]
```

### Key Engineering Features
1. **Lossless Intermediate Archival**: Live recordings are immediately preserved as uncompressed 16-bit PCM WAV files in `recordings/` with ISO timestamps, enabling post-test validation and replayability.
2. **Deterministic Parity**: Live and uploaded audio streams follow the exact same decoding, 22.05 kHz resampling, normalization, and feature extraction path.
3. **Responsive GUI**: Built with CustomTkinter, featuring real-time animated RMS waveform visualization during speech capture.
4. **Smart Audio Input Detection**: Automatically identifies external microphones (such as Blue Yeti or USB mics) and seamlessly falls back to OS defaults without crashing.
5. **Cross-Platform Standalone Deployment**: Ready-to-build configurations and automated GitHub Actions workflows for **Windows**, **Raspberry Pi OS**, and **macOS**.

---

## 📁 Repository Structure

```
Application/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── Outputs/                    # Standalone packaging configurations
│   ├── mac/                    # macOS bundle configuration
│   │   ├── main.spec           # PyInstaller spec for macOS .app
│   │   └── build_mac.sh        # 1-click macOS build script
│   ├── windows/                # Windows executable configuration
│   │   ├── main_windows.spec   # PyInstaller spec for Windows .exe
│   │   └── build_windows.bat   # 1-click Windows build batch script
│   ├── raspberry_pi/           # Raspberry Pi OS configuration
│   │   ├── main_rpi.spec       # PyInstaller spec for Linux ARM binary
│   │   └── build_rpi.sh        # 1-click Raspberry Pi setup & build script
│   └── ci/                     # GitHub Actions CI/CD template
│       └── build-executables.yml # Multi-platform workflow template
├── recordings/                 # Live recording archive (.gitkeep tracked)
└── test/                       # Sample validation audio files
```

---

## 📦 Standalone Executable Builds (No Python Required)

Pre-configured build scripts and PyInstaller specification files are provided for each operating system under [`Outputs/`](Outputs/):

### 1. macOS (`main.app`)
To build the standalone macOS Application Bundle:
```bash
cd Outputs/mac
./build_mac.sh
```
* **Output**: `Outputs/mac/dist/main.app`
* **Run**: Double-click `main.app` in Finder, or execute:
  ```bash
  open Outputs/mac/dist/main.app
  ```

---

### 2. Windows (`AccentClassifier.exe`)
To build the standalone Windows single-file executable:
1. Open Command Prompt or PowerShell on Windows.
2. Run the automated build batch script:
   ```cmd
   cd Outputs\windows
   build_windows.bat
   ```
* **Output**: `Outputs\windows\dist\AccentClassifier.exe`
* **Run**: Double-click `AccentClassifier.exe`. No Python installation required on the target PC.

---

### 3. Raspberry Pi OS (`AccentClassifier`)
Raspberry Pi OS requires native Linux audio libraries (`libportaudio2`, `libsndfile1`, `python3-tk`). The included shell script installs these system packages and compiles the standalone binary:
```bash
cd Outputs/raspberry_pi
chmod +x build_rpi.sh
./build_rpi.sh
```
* **Output**: `Outputs/raspberry_pi/dist/AccentClassifier`
* **Run**:
  ```bash
  ./Outputs/raspberry_pi/dist/AccentClassifier
  ```

---

### 4. Automated Cloud Builds (GitHub Actions Template)
A ready-to-use GitHub Actions workflow template is provided at [`Outputs/ci/build-executables.yml`](Outputs/ci/build-executables.yml). To enable automated cloud builds on GitHub:
1. Copy or move this file into your repository's `.github/workflows/` directory:
   ```bash
   mkdir -p .github/workflows
   cp Outputs/ci/build-executables.yml .github/workflows/
   ```
2. When pushed to GitHub (or triggered via GitHub's **Actions** tab), it spins up native virtual runners for **Windows**, **Linux/Raspberry Pi**, and **macOS**, compiling all three executables and uploading downloadable binaries automatically.

---

## 🛠️ Local Development & Setup

### Prerequisites
- Python 3.10 – 3.14
- PortAudio library (installed automatically via `sounddevice` wheels or package manager)

### 1. Clone the Repository
```bash
git clone https://github.com/Wixalot/CPE_Thesis_Accent-Classification-System.git
cd CPE_Thesis_Accent-Classification-System
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

---

## 🎤 Audio Hardware Configuration

In `audio/capture.py`:
- **`DEFAULT_AUDIO_DEVICE = "auto"`**: Automatically scans connected input hardware. If an external USB microphone (e.g., **Blue Yeti** or **USB PnP Audio Device**) is connected, it is automatically selected. If unplugged, it seamlessly falls back to the system default microphone.
- **Terminal Confirmation**: When recording starts, the active microphone index, device name, and sample rate are printed directly to the console:
  ```text
  🎤 Active Microphone: [Index 0] 'Yeti Stereo Microphone' (Sample Rate: 48000Hz)
  ```
- **Manual Device Override**: You can explicitly pass an integer device index or device name keyword to `DEFAULT_AUDIO_DEVICE` if needed.

---

## 📊 Model & Features
- **Sampling Rate**: Standardized to 22,050 Hz (mono).
- **Acoustic Features**: 78 total features:
  - 13 Mel-Frequency Cepstral Coefficients (MFCCs) (Mean & Std Dev = 26)
  - 13 First-Order Delta MFCCs (Mean & Std Dev = 26)
  - 13 Second-Order Delta-Delta MFCCs (Mean & Std Dev = 26)
- **Classifier**: Support Vector Classifier (`SVC(kernel='rbf')`) with `StandardScaler` normalization.
- **Accents**: Tagalog, Ilocano, Bisaya.

---

## 👥 Authors & Thesis Information
- **Institution**: Mapúa University - School of Electrical, Electronics, and Computer Engineering
- **Conference Publication**: ADMIT 2026
