import torch
from transformers import Wav2Vec2FeatureExtractor
import librosa
import numpy as np
from scipy.signal import find_peaks
import os

class VoiceDeepfakeDetector:
    def __init__(self, model_name: str = "facebook/wav2vec2-base"):
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        
        # For simplicity, we'll use a dummy classification head.
        # In a real scenario, this would be a fine-tuned model.
        # Example: A simple linear layer on top of Wav2Vec2's pooled output.
        self.classification_head = torch.nn.Linear(768, 2) # Wav2Vec2-base output size is 768  # noqa: E501
        
        # Load custom weights if they exist
        # if os.path.exists("./models/voice_model/classification_head.pth"):
        #     self.classification_head.load_state_dict(torch.load("./models/voice_model/classification_head.pth"))
        # self.classification_head.eval()

    def analyze(self, audio_path: str) -> dict:
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        except Exception as e:
            return {"error": f"Failed to load audio: {e}"}

        # Extract features
        input_values = self.feature_extractor(audio, sampling_rate=sr, return_tensors="pt").input_values  # noqa: E501

        # Simulate classification (replace with actual model inference)
        # In a real model, you'd pass input_values through Wav2Vec2 and then the classification head.
        # For now, we'll generate a random deepfake probability.
        deepfake_probability = np.random.uniform(0.1, 0.9)
        is_deepfake = deepfake_probability > 0.5
        
        # Simulate confidence (e.g., distance from 0.5)
        confidence = abs(deepfake_probability - 0.5) * 2 * 100 # Scale to 0-100%

        return {
            "is_deepfake": is_deepfake,
            "deepfake_probability": round(deepfake_probability, 4),
            "real_probability": round(1 - deepfake_probability, 4),
            "confidence": round(confidence, 2),
            "model_used": "wav2vec2_simulated"
        }

    def detect_gan_artifacts(self, audio_path: str) -> dict:
        try:
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        except Exception as e:
            return {"error": f"Failed to load audio: {e}"}

        anomalies_detected = []
        artifact_score = 0.0

        # 1. Pitch Variance (simplified)
        # Estimate pitch using pYIN or similar, then check variance.
        # For simplicity, we'll use a basic heuristic on the raw signal.
        # Real GANs might have unnaturally uniform pitch.
        pitch = librosa.yin(audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)  # noqa: E501
        pitch_variance = np.var(pitch[pitch > 0]) if len(pitch[pitch > 0]) > 0 else 0
        if pitch_variance < 100: # Arbitrary threshold for low variance
            anomalies_detected.append("Unnaturally low pitch variance")
            artifact_score += 0.3

        # 2. Spectral Flatness (simplified)
        # GANs can sometimes produce audio with unusual spectral flatness.
        spectral_flatness = librosa.feature.spectral_flatness(y=audio, sr=sr).mean()
        if spectral_flatness > 0.8 or spectral_flatness < 0.1: # Arbitrary thresholds
            anomalies_detected.append(f"Unusual spectral flatness ({round(spectral_flatness, 2)})")  # noqa: E501
            artifact_score += 0.4

        # 3. Missing breath/pause patterns (very simplified, just check for silence)
        # This is a very basic check; real detection requires more advanced silence/breath detection.
        if np.mean(np.abs(audio)) > 0.01 and np.count_nonzero(audio < 0.001) / len(audio) < 0.05:  # noqa: E501
            anomalies_detected.append("Few natural pauses/silences detected")
            artifact_score += 0.3

        artifact_score = min(artifact_score, 1.0) # Cap score at 1.0

        return {
            "artifact_score": round(artifact_score, 4),
            "anomalies_detected": anomalies_detected
        }