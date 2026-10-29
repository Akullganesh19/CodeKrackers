"""
Behavioral Anomaly Detection for API traffic.

Trains an ML model on normal API traffic patterns and flags unusual behavior
that deviates from the baseline. Uses scikit-learn Isolation Forest for
unsupervised anomaly detection on low-dimensional feature vectors.

Features extracted per request:
  - Request rate (requests per minute from IP)
  - Method entropy (unusual method for a given path)
  - Path depth / number of segments
  - Query parameter count & entropy
  - Body size (if applicable)
  - Header count & unusual header presence
  - Time of day (hour) deviation
  - User-agent entropy (unusual vs common)
"""
import os
import time
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
try:
    import numpy as np
except ImportError:
    np = None

try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None

from datetime import datetime

logger = logging.getLogger("vas.anomaly_detector")

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "anomaly_model.pkl"
FEATURE_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "feature_log.jsonl"

# Feature dimension
N_FEATURES = 14


class APIAnomalyDetector:
    """
    Lightweight unsupervised anomaly detector for API traffic.

    Maintains a rolling baseline of normal traffic and uses Isolation Forest
    to identify anomalous requests. The model is periodically retrained on
    new data to adapt to evolving traffic patterns.
    """

    def __init__(self):
        self.model = None
        self.is_trained = False
        self._request_buffer: List[np.ndarray] = []
        self._request_labels: List[str] = []
        self._buffer_max = 5000
        self._retrain_threshold = 1000  # New samples before retrain
        self._samples_since_train = 0

        # Per-IP rate tracking for feature extraction
        self._ip_rate_buckets: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=60)
        )
        # Path-frequency map for baseline
        self._path_counts: Dict[str, int] = defaultdict(int)
        self._total_requests = 0

        # Common user agents (for entropy calculation)
        self._common_uas = {
            "Mozilla/5.0", "Mozilla/4.0", "curl/", "python-requests",
            "PostmanRuntime", "Wget/", "okhttp/", "Go-http-client",
        }

        # Try to load existing model
        self._load_model()

    # ─── Feature Extraction ───────────────────────────────────────

    def extract_features(self, request_info: dict) -> np.ndarray:
        """
        Convert a request info dict into a fixed-length feature vector.

        request_info expected keys:
          - ip: str
          - method: str
          - path: str
          - query_params: dict or str
          - body_size: int (0 if no body)
          - user_agent: str
          - headers: dict
          - timestamp: float (time.time())
        """
        ip = request_info.get("ip", "unknown")
        method = request_info.get("method", "GET")
        path = request_info.get("path", "/")
        query_params = request_info.get("query_params", {})
        body_size = request_info.get("body_size", 0)
        user_agent = request_info.get("user_agent", "")
        headers = request_info.get("headers", {})
        ts = request_info.get("timestamp", time.time())

        if np is None:
            return None # Return None if numpy is not available

        features = np.zeros(N_FEATURES)
        idx = 0

        # [0] Request rate: requests from this IP in the last 60 seconds
        now = time.time()
        bucket = self._ip_rate_buckets[ip]
        bucket.append(now)
        # Count requests within the last 60s
        cutoff = now - 60
        rate = sum(1 for t in bucket if t > cutoff)
        features[idx] = min(rate / 100.0, 1.0)  # Normalize to [0,1]
        idx += 1

        # [1] Path depth: number of segments (normalized)
        segments = [s for s in path.split("/") if s]
        features[idx] = min(len(segments) / 10.0, 1.0)
        idx += 1

        # [2] Query parameter count (normalized)
        if isinstance(query_params, dict):
            qcount = len(query_params)
        elif isinstance(query_params, str):
            qcount = len(query_params.split("&")) if query_params else 0
        else:
            qcount = 0
        features[idx] = min(qcount / 10.0, 1.0)
        idx += 1

        # [3] Body size percentile (normalized to 1MB)
        features[idx] = min(body_size / 1_048_576.0, 1.0)
        idx += 1

        # [4] Method encoded: GET=0, POST=1, PUT=2, DELETE=3, PATCH=4, OPTIONS=5, HEAD=6, other=7
        method_map = {
            "GET": 0, "POST": 1, "PUT": 2, "DELETE": 3,
            "PATCH": 4, "OPTIONS": 5, "HEAD": 6,
        }
        features[idx] = method_map.get(method.upper(), 7) / 7.0
        idx += 1

        # [5] Header count (normalized)
        hcount = len(headers) if isinstance(headers, dict) else 0
        features[idx] = min(hcount / 20.0, 1.0)
        idx += 1

        # [6] User-agent entropy (0=common, 1=unusual/empty)
        ua_lower = (user_agent or "").lower()
        is_common = any(cua.lower() in ua_lower for cua in self._common_uas)
        features[idx] = 0.0 if is_common else (0.5 if ua_lower else 1.0)
        idx += 1

        # [7] Hour of day deviation (sin/cos encoding)
        dt = datetime.fromtimestamp(ts)
        hour_sin = np.sin(2 * np.pi * dt.hour / 24.0)
        hour_cos = np.cos(2 * np.pi * dt.hour / 24.0)
        features[idx] = (hour_sin + 1) / 2  # Normalize sin from [-1,1] to [0,1]
        idx += 1
        features[idx] = (hour_cos + 1) / 2  # Normalize cos from [-1,1] to [0,1]
        idx += 1

        # [9] Path rarity: how often has this path been seen
        self._total_requests += 1
        path_key = method.upper() + ":" + path
        self._path_counts[path_key] += 1
        path_freq = self._path_counts[path_key] / max(self._total_requests, 1)
        features[idx] = 1.0 - min(path_freq * 100, 1.0)  # 1=rare, 0=common
        idx += 1

        # [10] Query string entropy (character-level)
        qs_str = (
            json.dumps(query_params, sort_keys=True)
            if isinstance(query_params, dict)
            else str(query_params)
        )
        features[idx] = min(self._calc_entropy(qs_str) / 5.0, 1.0)
        idx += 1

        # [11] Suspicious characters in path (normalized count)
        suspicious_chars = sum(1 for c in path if c in "<>\"'`$|;&()[]{}\\%")
        features[idx] = min(suspicious_chars / 10.0, 1.0)
        idx += 1

        # [12] X-Forwarded-For / proxy header presence
        has_xff = 0
        if isinstance(headers, dict):
            has_xff = 1.0 if any(
                h.lower() in ("x-forwarded-for", "x-real-ip", "cf-connecting-ip")
                for h in headers
            ) else 0.0
        features[idx] = has_xff
        idx += 1

        # [13] Holiday/weekend indicator
        is_weekend = 1.0 if dt.weekday() >= 5 else 0.0
        features[idx] = is_weekend
        idx += 1

        return features

    def _calc_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        text_len = len(text)
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        entropy = -sum(
            (count / text_len) * np.log2(count / text_len)
            for count in freq.values()
        )
        return entropy

    # ─── Model Training ───────────────────────────────────────────

    def add_sample(self, features: np.ndarray, request_label: str = ""):
        """Add a feature vector to the training buffer."""
        self._request_buffer.append(features)
        self._request_labels.append(request_label)
        if len(self._request_buffer) > self._buffer_max:
            self._request_buffer.pop(0)
            self._request_labels.pop(0)

        self._samples_since_train += 1

        # Auto-retrain when enough new samples collected
        if self._samples_since_train >= self._retrain_threshold and self.is_trained:
            logger.info(
                "Auto-retraining anomaly model (%d new samples)",
                self._samples_since_train,
            )
            self.train()
            self._samples_since_train = 0

    def train(self, force: bool = False):
        """Train (or retrain) the Isolation Forest model on buffered data."""
        if len(self._request_buffer) < 100 and not force:
            logger.info(
                "Not enough samples to train anomaly model (%d < 100)",
                len(self._request_buffer),
            )
            return

        from sklearn.ensemble import IsolationForest

        X = np.array(self._request_buffer)
        logger.info("Training Isolation Forest on %d samples (dim=%d)", X.shape[0], X.shape[1])

        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.01,  # Expect ~1% anomalies
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X)
        self.is_trained = True
        self._samples_since_train = 0

        # Anomaly rate on training data
        preds = self.model.predict(X)
        anomaly_rate = (preds == -1).mean()
        logger.info("Model trained. Anomaly rate on training set: %.4f", anomaly_rate)

        self._save_model()

    def predict(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if a request is anomalous.

        Returns: (is_anomaly: bool, anomaly_score: float)
          - is_anomaly: True if the request is likely malicious
          - anomaly_score: Higher = more anomalous (0 to ~1)
        """
        if not self.is_trained or self.model is None:
            return False, 0.0

        X = features.reshape(1, -1)
        pred = self.model.predict(X)[0]
        score = self.model.score_samples(X)[0]

        # Normalize score to [0, 1] range (more negative = more anomalous)
        # Typical Isolation Forest scores range from ~-0.5 to ~0.5
        norm_score = min(max((-score + 0.5) / 1.0, 0.0), 1.0)

        is_anomaly = pred == -1
        return is_anomaly, norm_score

    # ─── Persistence ──────────────────────────────────────────────

    def _save_model(self):
        """Serialize model to disk."""
        if self.model is None:
            return
        try:
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(MODEL_PATH, "wb") as f:
                pickle.dump({
                    "model": self.model,
                    "n_features": N_FEATURES,
                    "n_samples": len(self._request_buffer),
                    "timestamp": time.time(),
                }, f)
            logger.info("Anomaly model saved to %s", MODEL_PATH)
        except Exception as e:
            logger.warning("Failed to save anomaly model: %s", e)

    def _load_model(self):
        """Load serialized model from disk."""
        if not MODEL_PATH.exists():
            logger.info("No existing anomaly model found at %s", MODEL_PATH)
            return
        try:
            with open(MODEL_PATH, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.is_trained = True
            logger.info(
                "Loaded anomaly model from %s (%d samples trained)",
                MODEL_PATH,
                data.get("n_samples", 0),
            )
        except Exception as e:
            logger.warning("Failed to load anomaly model: %s", e)

    def log_feature(self, request_info: dict, is_anomaly: bool, score: float):
        """Log feature vector and prediction for offline analysis."""
        try:
            FEATURE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "timestamp": request_info.get("timestamp", time.time()),
                "ip": request_info.get("ip", ""),
                "method": request_info.get("method", ""),
                "path": request_info.get("path", ""),
                "anomaly": is_anomaly,
                "score": round(score, 4),
                "features": self.extract_features(request_info).tolist(),
            }
            with open(FEATURE_LOG_PATH, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


# Singleton instance
_detector: Optional[APIAnomalyDetector] = None


def get_anomaly_detector() -> APIAnomalyDetector:
    """Get or create the global anomaly detector instance."""
    global _detector
    if _detector is None:
        _detector = APIAnomalyDetector()
        # Seed with initial training if not enough data
        if not _detector.is_trained and len(_detector._request_buffer) < 100:
            # Generate synthetic baseline data for initial training
            _seed_baseline(_detector)
    return _detector


def _seed_baseline(detector: APIAnomalyDetector):
    """Seed the detector with synthetic normal traffic for initial baseline."""
    import random

    normal_paths = [
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/api/threats"),
        ("GET", "/api/analytics/dashboard"),
        ("POST", "/api/detect/smishing"),
        ("POST", "/api/login/access-token"),
        ("GET", "/api/users/me"),
        ("GET", "/api/blacklist"),
        ("POST", "/api/spam/report"),
        ("GET", "/api/intel/phone"),
    ]

    common_uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "python-requests/2.31.0",
        "PostmanRuntime/7.36.0",
        "curl/8.4.0",
    ]

    for _ in range(200):
        method, path = random.choice(normal_paths)
        ua = random.choice(common_uas)
        info = {
            "ip": f"192.168.1.{random.randint(1, 254)}",
            "method": method,
            "path": path,
            "query_params": {},
            "body_size": random.randint(0, 1024) if method in ("POST", "PUT") else 0,
            "user_agent": ua,
            "headers": {"content-type": "application/json", "accept": "application/json"},
            "timestamp": time.time() - random.randint(0, 86400),
        }
        features = detector.extract_features(info)
        detector.add_sample(features, f"seed:{method}:{path}")

    detector.train(force=True)
    logger.info("Anomaly detector seeded with synthetic baseline data")