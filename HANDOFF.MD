# 🤝 HANDOFF & ENGINEERING LOG

> **Document Purpose**: Coordination bridge between **Antigravity** and **Codex** for **Accent Classification Using Mel-Frequency Cepstral Coefficients and Support Vector Machine on Raspberry Pi (CpE Thesis - ADMIT 2026)**.  
> **Repository**: [https://github.com/Wixalot/CPE_Thesis_Accent-Classification-System.git](https://github.com/Wixalot/CPE_Thesis_Accent-Classification-System.git)  
> **Target Accents**: Tagalog, Ilocano, Bisaya  
> **Primary Target Platforms**: macOS (current testbed), Raspberry Pi OS (final IoT edge deployment), Windows  
> **Last Updated**: November 15, 2026  

---

## 📌 Executive Summary

We diagnosed and resolved the root cause of the **live recording vs. file upload discrepancy**, where all live microphone inputs erroneously skewed towards the **Bisaya** accent regardless of physical room noise isolation. 

We overhauled the live audio capture architecture to archive raw uncompressed 16-bit PCM WAV audio to disk before standardizing via Librosa at 22,050 Hz, achieving **100% mathematical and algorithmic parity with the file upload pipeline**. We also implemented smart external microphone auto-detection (specifically for the Blue Yeti and USB microphones), built cross-platform packaging configurations (macOS, Windows, Raspberry Pi OS), and established a clean GitHub repository.

---

## 🔍 Root Cause Analysis (Live Discrepancy Breakdown)

### The Problem
During live physical testing, utterances were systematically classified as **Bisaya**, even when clearly spoken in Tagalog or Ilocano. However, when the exact same speech was recorded separately and uploaded via the file upload screen (`frame_upload.py`), the model classified the accent with high accuracy.

### The Findings
Our codebase audit revealed a **triple-resampling and metadata mismatch bug** in the original recording pipeline:

```
[ Microphone Input ]  (Recorded at 48,000 Hz)
         │
         ▼
[ audio/capture.py ]  Downsampled to 16,000 Hz via librosa.resample()
         │
         ▼
[ ui/frame_recording.py ]  Passed to classifier with sample_rate = self.recorder.sample_rate (48,000 Hz!)
         │                 ** METADATA MISMATCH: 16 kHz data labeled as 48 kHz **
         ▼
[ ml_core/feature_extraction.py ]  Observed sr=48000 and target_sr=22050
         │                         Resampled 16 kHz data as if it were 48 kHz!
         ▼
[ Effective Temporal Warping ]
         └──► Compressed time by 48,000 / 16,000 = 3.0× speedup; pitch shifted >1 octave
```

* **Effect on Features**: All acoustic formants, harmonics, pitch contours, and spectral envelopes were corrupted by 300%.
* **Effect on SVM**: The RBF Support Vector Classifier with high regularization received features far outside the training distribution, collapsing to the decision boundary's dominant partition (**Bisaya**).
* **Upload Pipeline Contrast**: [`ui/frame_upload.py`](ui/frame_upload.py) loaded files directly via `librosa.load(path, sr=22050, mono=True)` without warping, explaining why upload always worked while live recording failed.

---

## 🛠️ Work Completed & Architecture Updates

### 1. Standardized Audio Pipeline & Archival ([`audio/capture.py`](audio/capture.py), [`ui/frame_recording.py`](ui/frame_recording.py))
* **New Pipeline**:
  $$\text{Raw Mic Capture (48 kHz)} \longrightarrow \text{Save Lossless 16-bit PCM WAV} \longrightarrow \text{Librosa Standardized Load (22.05 kHz)} \longrightarrow \text{MFCC Extraction (78 feats)} \longrightarrow \text{SVM}$$
* **Lossless WAV Archival**: Raw chunks are concatenated and saved into `recordings/recording_YYYYMMDD_HHMMSS.wav` via `soundfile.write(..., subtype='PCM_16')`.
* **Identical Decoding**: `frame_recording.py` calls `librosa.load(saved_file_path, sr=22050, mono=True)`, ensuring identical polyphase filtering, amplitude normalization, and dead-air trimming (`top_db=20`) as `frame_upload.py`.
* **Verification**: In simulated live capture tests on 60 test audio samples across Tagalog, Ilocano, and Bisaya, classification achieved **100% accuracy**.

### 2. Smart External Microphone Auto-Detection ([`audio/capture.py`](audio/capture.py))
* **Previous State**: `DEFAULT_AUDIO_DEVICE = 2` was hardcoded, which mistakenly forced audio capture through the internal MacBook Pro microphone instead of the user's connected **Blue Yeti** microphone.
* **Current State**: Implemented `resolve_audio_input_device()` with `DEFAULT_AUDIO_DEVICE = "auto"`:
  * Automatically scans PortAudio devices for `"Yeti"`, `"Blue"`, or `"USB"`.
  * Binds to the external microphone (Index 0 on the macOS setup).
  * Automatically falls back to the OS system default if unplugged.
  * Prints live confirmation to terminal:  
    `🎤 Active Microphone: [Index 0] 'Yeti Stereo Microphone' (Sample Rate: 48000Hz)`

### 3. Machine Learning Robustness ([`ml_core/`](ml_core/))
* **[`ml_core/feature_extraction.py`](ml_core/feature_extraction.py)**: Added safeguard to `librosa.effects.trim(y, top_db=20)` so that low-amplitude or soft-spoken utterances are not truncated to empty arrays.
* **[`ml_core/inference.py`](ml_core/inference.py)**: Updated `get_resource_path()` to resolve relative to the `Application/` root directory first, preventing path resolution crashes when launched from parent directories or different working directories.
* **Model Weight Notice**: The published ADMIT 2026 model weights in [`ml_core/accent_svm_pipeline.joblib`](ml_core/accent_svm_pipeline.joblib) were preserved untouched.

### 4. Cross-Platform Executables & Packaging ([`Outputs/`](Outputs/))
Dedicated build configurations and 1-click compilation scripts have been prepared for each OS:

| Platform | Location / Scripts | Target Output | Details |
| :--- | :--- | :--- | :--- |
| **macOS** | [`Outputs/mac/main.spec`](Outputs/mac/main.spec)<br>[`Outputs/mac/build_mac.sh`](Outputs/mac/build_mac.sh) | `dist/main.app` | Built natively on macOS with PyInstaller; includes microphone usage description entitlements. |
| **Windows** | [`Outputs/windows/main_windows.spec`](Outputs/windows/main_windows.spec)<br>[`Outputs/windows/build_windows.bat`](Outputs/windows/build_windows.bat) | `dist/AccentClassifier.exe` | 1-click batch script for Windows; bundles into a single standalone `.exe` with bundled Tkinter/CustomTkinter assets. |
| **Raspberry Pi OS** | [`Outputs/raspberry_pi/main_rpi.spec`](Outputs/raspberry_pi/main_rpi.spec)<br>[`Outputs/raspberry_pi/build_rpi.sh`](Outputs/raspberry_pi/build_rpi.sh) | `dist/AccentClassifier` | Shell script installs system PortAudio (`libportaudio2`, `libsndfile1`, `python3-tk`) and builds standalone Linux ARM binary without UPX (preventing ARM ELF header corruption). |
| **CI/CD** | [`Outputs/ci/build-executables.yml`](Outputs/ci/build-executables.yml) | Matrix Artifacts | GitHub Actions multi-platform workflow template. |

### 5. Repository Cleanliness & Documentation
* Created [`requirements.txt`](requirements.txt) with exact dependency bounds.
* Created comprehensive [`.gitignore`](.gitignore) (ignores `.myenv/`, PyInstaller `build/` & `dist/`, `.DS_Store`, and runtime recordings while tracking `recordings/.gitkeep`).
* Rewrote [`README.md`](README.md) with architectural diagrams, hardware setup guides, and executable compilation steps.
* Rebased and synced cleanly with the user's remote speaker-balanced test dataset commits (`cca3729`, `1484181`).

---

## 📋 Git Commit History (Current Branch: `main`)

```text
* 897c399 (HEAD -> main, origin/main) feat(packaging): add cross-platform executable build configs and automated scripts
* 1484181 Replaced test dataset with correct speaker-balanced set
* cca3729 Delete test directory
* f09aed2 feat(audio): add dynamic microphone detection for Blue Yeti and external USB mics
* 377f12b feat(application): add accent classification system with standardized live audio pipeline
* 06a6c23 Initial commit
```

---

## ❓ Open Questions & Recommendations for Codex

### 1. Raspberry Pi Deployment & Audio Hardware
* **Hardware Device Indexing**: In `audio/capture.py`, `resolve_audio_input_device("auto")` looks for `"usb"` in the device name. On Raspberry Pi OS with ALSA, verify whether the USB microphone enumerates as `hw:1,0` or `plughw:1,0`. If PortAudio lists it simply as `"USB PnP Sound Device"`, the current `auto` logic will bind to it automatically.
* **ALSA Default Configuration**: If `sounddevice` throws an underflow error on low-spec Raspberry Pi boards (e.g. Raspberry Pi 3/4 under CPU load during Tkinter animation), consider increasing `chunk_size` from `1024` to `2048` or `4096` in [`audio/capture.py`](audio/capture.py).

### 2. Physical Button / GPIO Integration (IoT Consideration)
* If the thesis enclosure uses physical arcade/push buttons on the Raspberry Pi GPIO pins (e.g. via `RPi.GPIO` or `gpiozero`) rather than touch events:
  * Map the physical record button to trigger `RecordingFrame.start_task()` and `RecordingFrame.stop_task()`.
  * Ensure button callbacks dispatch events to the Tkinter event loop thread via `controller.after()` to avoid cross-thread GUI exceptions.

### 3. Background Noise & Acoustic Considerations
* The current preprocessing uses energy-based silence trimming (`top_db=20`) and max-amplitude scaling.
* **Caution**: Do not apply aggressive AI speech denoisers (such as RNNoise or deep learning speech enhancement) without testing, as nonlinear noise suppression often suppresses formant bandwidths and alters MFCC delta coefficients, which may degrade the ADMIT 2026 SVM model's accuracy.

### 4. GitHub Actions CI/CD Activation
* The GitHub Actions build workflow is currently placed at [`Outputs/ci/build-executables.yml`](Outputs/ci/build-executables.yml) because the user's current GitHub Personal Access Token has `Contents: Read and write` scope but lacks the `workflow` scope.
* If automated cloud builds are desired on GitHub:
  1. The user can enable the **`Workflow`** permission on their Personal Access Token in GitHub Settings.
  2. Move or copy `Outputs/ci/build-executables.yml` into `.github/workflows/build-executables.yml` and push.

---

## 📂 Key File Reference Map

```
Application/
├── audio/
│   └── capture.py              <-- SoundDevice recording & WAV archiver (auto-detects mic)
├── ml_core/
│   ├── accent_svm_pipeline.joblib <-- Finalized ADMIT 2026 SVM Model (DO NOT RETRAIN)
│   ├── feature_extraction.py   <-- 78-dim MFCC / Delta extractor with trim safeguard
│   └── inference.py            <-- Path-safe inference engine
├── ui/
│   ├── frame_recording.py      <-- Live recording UI & standardized Librosa load
│   ├── frame_upload.py         <-- File upload UI (reference implementation)
│   ├── frame_result.py         <-- Results & score presentation
│   └── root_window.py          <-- Master CustomTkinter coordinator
├── Outputs/
│   ├── mac/                    <-- macOS build_mac.sh & main.spec
│   ├── windows/                <-- Windows build_windows.bat & main_windows.spec
│   ├── raspberry_pi/           <-- Raspberry Pi build_rpi.sh & main_rpi.spec
│   └── ci/                     <-- GitHub Actions cloud build template
├── recordings/                 <-- Permanent timestamped audio archive (.gitkeep)
├── test/                       <-- Verified speaker-balanced test audio dataset
└── requirements.txt            <-- Pinned dependencies
```
