# ml_core/feature_extraction.py
import librosa
import numpy as np


def extract_live_audio_features(y: np.ndarray, sr: int = 22050, n_mfcc: int = 13) -> np.ndarray:
    try:
        # 1. Flatten to 1D array
        if y.ndim > 1:
            y = y.flatten()

        # 2. STRIP DEAD AIR: Automatically trim leading/trailing silence (below 20 decibels)
        trimmed_y, _ = librosa.effects.trim(y, top_db=20)
        if len(trimmed_y) > 0:
            y = trimmed_y

        # 3. RESAMPLE TO TRAINING RATE: Keep live input and uploaded input on the same scale
        target_sr = 22050
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        
        # 4. NORMALIZE VOLUME: Scale the amplitude to exactly match librosa.load's default behavior
        if np.max(np.abs(y)) > 0:
            y = y / np.max(np.abs(y))

        # --- The exact feature extraction from your training script ---
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        delta_mfccs = librosa.feature.delta(mfccs)
        delta2_mfccs = librosa.feature.delta(mfccs, order=2)


        feature_chunks = []
        
        for feat in [mfccs, delta_mfccs, delta2_mfccs]:
            feature_chunks.extend(np.mean(feat, axis=1))
            feature_chunks.extend(np.std(feat, axis=1))


        features = np.nan_to_num(np.array(feature_chunks, dtype=np.float32))
        return features.reshape(1, -1)  

    except Exception as e:
        print(f"Feature Extraction Error: {e}")
        return None