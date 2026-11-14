"""Conservative audio quality control for accent assessment.

The SVM was trained on natural speech MFCCs.  This module deliberately avoids
AI speech enhancement and aggressive denoising because either can change
formants and MFCC delta features.  It only removes sub-speech rumble and, when
there is enough leading/trailing non-speech audio to estimate stationary noise,
applies a capped spectral attenuation.
"""

from __future__ import annotations

from typing import Any

import librosa
import numpy as np
from scipy.signal import butter, sosfiltfilt


TARGET_SAMPLE_RATE = 22050
MIN_AUDIO_SECONDS = 0.75
MIN_NOISE_FRAMES = 6
MIN_ACCEPTABLE_SNR_DB = 6.0
WARNING_SNR_DB = 12.0


def _empty_quality(message: str) -> dict[str, Any]:
    return {
        "accepted": False,
        "noise_reduction_applied": False,
        "filters_applied": [],
        "snr_db": None,
        "message": message,
    }


def prepare_audio_for_assessment(
    audio_data: np.ndarray, sample_rate: int = TARGET_SAMPLE_RATE
) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Return assessment-ready mono audio and an honest quality report.

    A quality rejection is preferable to applying strong suppression that would
    make the model evaluate acoustically altered speech.  If a reliable noise
    profile cannot be found, the audio is left otherwise untouched after a
    low-frequency rumble filter and is not penalized for that absence.
    """
    if audio_data is None:
        return None, _empty_quality("No audio was received.")

    y = np.asarray(audio_data, dtype=np.float32).reshape(-1)
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)

    if sample_rate != TARGET_SAMPLE_RATE:
        y = librosa.resample(y, orig_sr=sample_rate, target_sr=TARGET_SAMPLE_RATE)
        sample_rate = TARGET_SAMPLE_RATE

    if y.size < int(MIN_AUDIO_SECONDS * sample_rate):
        return None, _empty_quality("Recording is too short. Please speak for at least one second.")

    peak = float(np.max(np.abs(y)))
    if peak < 1e-5:
        return None, _empty_quality("No audible speech was detected. Please record again.")

    # A gentle 2nd-order high-pass removes DC offset, handling noise, and room
    # rumble below the normal speech band without reshaping speech formants.
    sos = butter(2, 70.0, btype="highpass", fs=sample_rate, output="sos")
    y = sosfiltfilt(sos, y).astype(np.float32)

    frame_length = 1024
    hop_length = 256
    rms = librosa.feature.rms(
        y=y, frame_length=frame_length, hop_length=hop_length, center=True
    )[0]
    # Estimate stationary background only from frames *outside* the speech
    # intervals.  Using merely the quietest percentile is unsafe: soft vowels
    # can be mistaken for noise and then subtracted from the speaker.
    speech_intervals = librosa.effects.split(
        y, top_db=10, frame_length=frame_length, hop_length=hop_length
    )
    frame_centers = librosa.frames_to_samples(
        np.arange(len(rms)), hop_length=hop_length
    )
    speech_frames = np.zeros(len(rms), dtype=bool)
    for start, end in speech_intervals:
        speech_frames |= (frame_centers >= start) & (frame_centers < end)
    quiet_frames = ~speech_frames

    quality: dict[str, Any] = {
        "accepted": True,
        "noise_reduction_applied": False,
        "filters_applied": ["highpass_70hz"],
        "snr_db": None,
        "message": "Conservative low-frequency noise filtering applied.",
    }

    if np.count_nonzero(quiet_frames) < MIN_NOISE_FRAMES or np.count_nonzero(speech_frames) < 3:
        return y, quality

    noise_rms = float(np.median(rms[quiet_frames]))
    speech_rms = float(np.median(rms[speech_frames]))
    snr_db = 20.0 * np.log10(max(speech_rms, 1e-10) / max(noise_rms, 1e-10))
    quality["snr_db"] = float(snr_db)

    if snr_db < MIN_ACCEPTABLE_SNR_DB:
        return None, _empty_quality(
            f"Background noise is too high ({snr_db:.1f} dB estimated SNR). "
            "Please move to a quieter place and try again."
        )

    # Do not alter already-clean speech.  Running any spectral gate when the
    # estimated SNR is healthy only moves MFCCs away from the training audio.
    if snr_db >= WARNING_SNR_DB:
        quality["message"] = f"Audio quality acceptable (estimated SNR: {snr_db:.1f} dB)."
        return y, quality

    # Spectral attenuation is deliberately capped at 20%, retaining at least
    # 80% of every time-frequency bin.  This removes part of stationary noise
    # while preserving the spectral envelope the MFCC/SVM model learned from.
    spectrum = librosa.stft(y, n_fft=frame_length, hop_length=hop_length, center=True)
    magnitude = np.abs(spectrum)
    noise_spectrum = np.median(magnitude[:, quiet_frames], axis=1, keepdims=True)
    gain = np.maximum(0.80, 1.0 - 0.20 * noise_spectrum / (magnitude + 1e-10))
    y = librosa.istft(spectrum * gain, hop_length=hop_length, length=len(y)).astype(np.float32)
    quality["noise_reduction_applied"] = True
    quality["filters_applied"].append("spectral_reduction")
    quality["message"] = (
        "Conservative stationary-noise reduction applied"
        + (f" (estimated SNR: {snr_db:.1f} dB)." if snr_db < WARNING_SNR_DB else ".")
    )
    return y, quality
