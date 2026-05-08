import whisper
import os

class AudioTranscriber:
    def __init__(self):
        """
        Initializes the Whisper model. 
        The model size is determined by the WHISPER_MODEL_SIZE environment variable.
        Valid sizes: 'tiny', 'base', 'small', 'medium', 'large'.
        """
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        # Load model into memory. Requires FFmpeg to be installed on the system.
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribes the given audio file and detects the language.
        Returns a structured dictionary with text, language, and word-level data.
        """
        # Run inference with word_timestamps=True for forensic detail
        result = self.model.transcribe(
            audio_path, 
            language=None,  # Enables automatic language detection
            task="transcribe",
            word_timestamps=True
        )
        
        # Flatten word-level data from segments for easier analysis
        all_words = []
        for segment in result.get("segments", []):
            if "words" in segment:
                all_words.extend(segment["words"])

        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "words": all_words
        }

    def extract_flagged_phrases(self, transcript: str) -> list[dict]:
        """
        Scans the transcript for high-risk vishing phrases categorized by threat type.
        """
        risk_dictionary = {
            "Authority": ["i am calling from", "trai", "cbi", "police", "court notice", "legal action", "arrest warrant"],
            "Financial": ["send money", "transfer", "otp", "upi pin", "card number", "cvv", "account blocked"],
            "Urgency": ["immediately", "within 2 hours", "or else", "last warning", "final notice"]
        }
        
        flagged_hits = []
        text_lower = transcript.lower()
        
        for category, phrases in risk_dictionary.items():
            for phrase in phrases:
                start = 0
                while (idx := text_lower.find(phrase, start)) != -1:
                    flagged_hits.append({
                        "phrase": phrase,
                        "category": category,
                        "start_index": idx,
                        "end_index": idx + len(phrase)
                    })
                    start = idx + len(phrase)
                    
        return flagged_hits