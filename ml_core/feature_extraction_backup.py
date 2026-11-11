# ml_core/feature_extraction.py
import librosa
import numpy as np


def extract_live_audio_features(y: np.ndarray, sr: int = 22050, n_mfcc: int = 13) -> np.ndarray:
    try:
        # 1. Flatten to 1D array
        if y.ndim > 1:
            y = y.flatten()

        # 2. STRIP DEAD AIR: Automatically trim leading/trailing silence (below 20 decibels)
        y, _ = librosa.effects.trim(y, top_db=20)

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

        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        rms = librosa.feature.rms(y=y)

        feature_chunks = []
        
        for feat in [mfccs, delta_mfccs, delta2_mfccs]:
            feature_chunks.extend(np.mean(feat, axis=1))
            feature_chunks.extend(np.std(feat, axis=1))

        for feat in [chroma, spectral_contrast]:
            feature_chunks.extend(np.mean(feat, axis=1))
            feature_chunks.extend(np.std(feat, axis=1))

        for feat in [spectral_centroid, spectral_bandwidth, spectral_rolloff, zero_crossing_rate, rms]:
            feature_chunks.append(float(np.mean(feat)))
            feature_chunks.append(float(np.std(feat)))

        features = np.nan_to_num(np.array(feature_chunks, dtype=np.float32))
        return features.reshape(1, -1)  

    except Exception as e:
        print(f"Feature Extraction Error: {e}")
        return None