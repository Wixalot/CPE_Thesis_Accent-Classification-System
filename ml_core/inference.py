# ml_core/inference.py
import sys
import os
import joblib
import numpy as np
from pathlib import Path
from .feature_extraction import extract_live_audio_features

def get_resource_path(relative_path):
    """
    Dynamically finds the absolute path to resources.
    Works for raw Python execution (from any CWD) and compiled PyInstaller apps.
    """
    if getattr(sys, 'frozen', False):
        # If running as a compiled PyInstaller app, it uses the temporary MEIPASS folder
        base_path = Path(sys._MEIPASS)
        return str(base_path / relative_path)
    else:
        # Check relative to Application package root first
        app_root = Path(__file__).resolve().parent.parent
        candidate = app_root / relative_path
        if candidate.exists():
            return str(candidate)
        
        # Fallback to current working directory
        cwd_candidate = Path(os.getcwd()) / relative_path
        if cwd_candidate.exists():
            return str(cwd_candidate)
            
        return str(candidate)

class AccentClassifier:
    def __init__(self, model_path="ml_core/accent_svm_pipeline.joblib"):
        # We process the path through the dynamic resolver before loading
        absolute_model_path = get_resource_path(model_path)
        
        try:
            pipeline = joblib.load(absolute_model_path)
            # Unpacking the dictionary you created in train_svm_Additions.py
            self.scaler = pipeline['scaler'] 
            self.model = pipeline['model']
            self.is_ready = True
            print(f"AI Pipeline loaded successfully from: {absolute_model_path}")
        except Exception as e:
            print(f"Failed to load AI model from {absolute_model_path}: {e}")
            self.is_ready = False

    def predict(self, audio_data: np.ndarray, sample_rate: int = 22050):
        if not self.is_ready or audio_data is None:
            return "ERROR: MODEL NOT LOADED"

        # 1. Extract the features
        features = extract_live_audio_features(audio_data, sr=sample_rate)
        if features is None:
            return "ERROR: EXTRACTION FAILED"

        # 2. Reshape for Sklearn (it expects a 2D array of shape [1, N_features])
        features_reshaped = features.reshape(1, -1)

        # 3. Apply the exact scaling used in training
        features_scaled = self.scaler.transform(features_reshaped)

        # 4. Predict
        prediction = self.model.predict(features_scaled)
        
        # Returns the raw string (e.g., 'Tagalog', 'Bisaya', 'Ilocano')
        return prediction[0]

    def predict_with_scores(self, audio_data: np.ndarray, sample_rate: int = 22050):
        if not self.is_ready or audio_data is None:
            return "ERROR: MODEL NOT LOADED", {}

        features = extract_live_audio_features(audio_data, sr=sample_rate)
        if features is None:
            return "ERROR: EXTRACTION FAILED", {}

        features_reshaped = features.reshape(1, -1)
        features_scaled = self.scaler.transform(features_reshaped)

        prediction = self.model.predict(features_scaled)[0]
        decision_scores = self.model.decision_function(features_scaled)
        score_values = decision_scores[0] if getattr(decision_scores, "ndim", 0) > 1 else decision_scores

        class_scores = {
            label: float(score)
            for label, score in zip(self.model.classes_, score_values)
        }

        return prediction, class_scores