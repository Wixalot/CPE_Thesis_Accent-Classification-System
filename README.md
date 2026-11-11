# Real-Time Accent Classification System

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
4. **Hardware Flexibility**: Configured for testing on macOS with automatic fallback and seamless migration to Raspberry Pi USB microphones.

---

## 📁 Repository Structure

```
Application/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── ui/                         # CustomTkinter GUI implementation
│   ├── root_window.py          # Master window & frame coordinator
│   ├── theme.py                # Color palette & typography
│   ├── frame_home.py           # Screen 1: Mode selector (Record / Upload)
│   ├── frame_recording.py      # Screen 2: Real-time recording & animated waveform
│   ├── frame_upload.py         # Screen 3: File picker & upload processing
│   └── frame_result.py         # Screen 4: Prediction & class scores display
├── audio/                      # Audio capture subsystem
│   └── capture.py              # SoundDevice background worker & WAV archiver
├── ml_core/                    # Machine Learning subsystem
│   ├── accent_svm_pipeline.joblib  # Trained model & scaler (ADMIT 2026)
│   ├── feature_extraction.py   # MFCC, Delta, Delta-Delta feature extractor
│   └── inference.py            # Model loader & inference wrapper
├── recordings/                 # Live recording archive (.gitkeep tracked)
└── test/                       # Sample validation audio files
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 – 3.14
- PortAudio library (installed automatically via `sounddevice` wheels or via package manager)

### 1. Clone the Repository
```bash
git clone https://github.com/Wixalot/CPE_Thesis_Accent-Classification-System.git
cd CPE_Thesis_Accent-Classification-System
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the desktop interface with:
```bash
python main.py
```

### Hardware Configuration (macOS vs. Raspberry Pi)
In `audio/capture.py`:
- **macOS Testing Setup**: `DEFAULT_AUDIO_DEVICE = 2` (configured for current test machine).
- **Raspberry Pi Deployment**: Set `DEFAULT_AUDIO_DEVICE = None` (uses system default USB microphone) or query available devices with:
  ```python
  import sounddevice as sd
  print(sd.query_devices())
  ```
  and set `DEFAULT_AUDIO_DEVICE` to the corresponding device index.
- If the specified device index is unavailable, the application gracefully logs a warning and falls back to the system default microphone without crashing.

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
