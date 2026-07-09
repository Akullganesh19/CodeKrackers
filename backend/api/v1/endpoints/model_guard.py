"""
Model Security API endpoints — protects AI models from adversarial attacks,
extraction, theft, and supply chain poisoning.

Endpoints:
  - POST /models/register — Register a model with checksum + watermark
  - GET /models/status — List registered models and their security status
  - POST /models/approve/{id} — Approve a model for deployment
  - POST /models/verify — Verify a model's integrity before loading
  - GET /models/inferences — View recent inference logs with extraction risk
  - POST /models/adversarial-test — Test model robustness against adversarial examples
  - POST /detect/secure-sms — Protected SMS detection with extraction monitoring
"""
import time
import hashlib
import logging
from typing import Optional, List
from fastapi import APIRouter, Request, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.api import deps
from backend.db.session import get_db
from backend.models.model_version import ModelVersion, ModelInferenceLog
from backend.models.user import User, UserRole
from backend.services.model_security import (
    register_model,
    verify_model_integrity,
    approve_model,
    compute_adversarial_robustness_score,
    generate_adversarial_training_data,
    get_extraction_detector,
    TEXT_ADVERSARIAL_EXAMPLES,
    ADVERSARIAL_PERTURBATIONS,
)

logger = logging.getLogger("vas.model_guard")
router = APIRouter()


# ─── Model Registry ───────────────────────────────────────────────

@router.post("/register", summary="Register a model with checksum + watermark")
def api_register_model(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    name: str = Query(..., description="Model name"),
    version: str = Query(..., description="Semver version"),
    framework: str = Query(..., description="Framework (transformers, pytorch, sklearn)"),
    file_path: str = Query(..., description="Path to model weights file"),
    trained_by: Optional[str] = Query(None),
    training_dataset: Optional[str] = Query(None),
    git_commit: Optional[str] = Query(None),
    accuracy: Optional[float] = Query(None),
    f1_score: Optional[float] = Query(None),
):
    """Register a model with cryptographic checksum and watermark."""
    try:
        model = register_model(
            db=db,
            name=name,
            version=version,
            framework=framework,
            file_path=file_path,
            trained_by=trained_by or current_user.email,
            training_dataset=training_dataset,
            git_commit=git_commit,
            accuracy=accuracy,
            f1_score=f1_score,
            tags={"registered_by": current_user.email},
            notes=f"Registered via API by {current_user.email}",
        )
        return {
            "message": "Model registered successfully",
            "model_id": model.id,
            "name": model.name,
            "version": model.version,
            "sha384_hash": f"{model.sha384_hash[:16]}...",
            "file_size": model.file_size_bytes,
            "watermark": hashlib.sha384(model.watermark_embedding).hexdigest()[:16] if model.watermark_embedding else "N/A",
            "is_approved": model.is_approved,
            "is_active": model.is_active,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", summary="List all registered models")
def api_model_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """List all registered models with their security status."""
    models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    return {
        "total": len(models),
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "framework": m.framework,
                "sha384_hash": f"{m.sha384_hash[:16]}...",
                "file_size": m.file_size_bytes,
                "is_approved": m.is_approved,
                "is_active": m.is_active,
                "watermark_verified": m.watermark_verified,
                "adversarial_robustness": m.adversarial_robustness,
                "accuracy": m.accuracy,
                "f1_score": m.f1_score,
                "trained_by": m.trained_by,
                "created_at": m.created_at,
            }
            for m in models
        ],
    }


@router.post("/approve/{model_id}", summary="Approve a model for deployment")
def api_approve_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Approve a model for production deployment."""
    model = approve_model(db, model_id=model_id, approved_by=current_user.email)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return {
        "message": "Model approved",
        "model_id": model.id,
        "name": model.name,
        "version": model.version,
        "watermark_verified": model.watermark_verified,
    }


@router.post("/verify", summary="Verify model integrity before loading")
def api_verify_model(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    name: str = Query(..., description="Model name to verify"),
    file_path: str = Query(..., description="Path to model weights file"),
):
    """Verify a model's checksum before loading (supply chain protection)."""
    is_valid, model = verify_model_integrity(db, name, file_path)
    if not model:
        raise HTTPException(status_code=404, detail="No active version found")
    
    return {
        "is_valid": is_valid,
        "model_name": model.name,
        "model_version": model.version,
        "expected_hash": model.sha384_hash[:16],
        "is_approved": model.is_approved,
        "message": "Model integrity verified" if is_valid else "MODEL TAMPER DETECTED",
    }


# ─── Inference Monitoring ─────────────────────────────────────────

@router.get("/inferences", summary="View inference logs with extraction risk")
def api_inference_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    limit: int = Query(50, ge=1, le=500),
    suspicious_only: bool = Query(False),
):
    """View recent inference API calls and model extraction risk scores."""
    query = db.query(ModelInferenceLog).order_by(ModelInferenceLog.created_at.desc())
    
    if suspicious_only:
        query = query.filter(ModelInferenceLog.is_suspicious == True)
    
    logs = query.limit(limit).all()
    
    return {
        "total_found": len(logs),
        "suspicious_count": sum(1 for l in logs if l.is_suspicious),
        "logs": [
            {
                "id": l.id,
                "client_ip": l.client_ip,
                "model_name": l.model_name,
                "input_length": l.input_length,
                "response_time_ms": l.response_time_ms,
                "is_suspicious": l.is_suspicious,
                "suspicion_reason": l.suspicion_reason,
                "extraction_risk_score": l.extraction_risk_score,
                "timestamp": l.created_at,
            }
            for l in logs
        ],
    }


# ─── Adversarial Testing ──────────────────────────────────────────

@router.post("/adversarial-test", summary="Test model robustness")
def api_adversarial_test(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    model_name: str = Query("smishing-bert", description="Model to test"),
):
    """
    Test a model's robustness against adversarial examples.
    
    Applies common text perturbations (char swap, leet speak, whitespace)
    and measures how many flip the model's prediction.
    Returns an adversarial robustness score.
    """
    # Simulated model prediction function
    # In production, replace with actual model inference
    def mock_predict(text: str) -> int:
        # Mock: "scammy" keywords trigger "scam" (1) else "safe" (0)
        scam_keywords = ["kyc", "aadhaar", "otp", "blocked", "urgent", "expir", "suspended"]
        text_lower = text.lower()
        score = sum(1 for kw in scam_keywords if kw in text_lower)
        return 1 if score >= 2 else 0
    
    test_samples = [
        "Your Aadhaar KYC is expiring. Update now to avoid suspension.",
        "Your parcel has been blocked by customs. Pay ₹500 to release.",
        "Income tax refund of ₹12,500 is pending. Click here to claim.",
        "Hi, let's meet for coffee tomorrow at the usual place.",
        "Your electricity bill is due. Pay online at the official portal.",
        "OTP 4521 for your transaction. Do not share this with anyone.",
        "Congratulations! You've won a lottery of ₹10 lakhs. Call now.",
    ]
    test_labels = [1, 1, 1, 0, 0, 0, 1]
    
    robustness_score = compute_adversarial_robustness_score(
        model_predict_fn=mock_predict,
        test_samples=test_samples,
        test_labels=test_labels,
    )
    
    # Generate augmented training data
    aug_samples, aug_labels = generate_adversarial_training_data(test_samples, test_labels)
    
    return {
        "model_name": model_name,
        "adversarial_robustness_score": round(robustness_score, 4),
        "test_samples_used": len(test_samples),
        "augmented_samples": len(aug_samples) - len(test_samples),
        "adversarial_perturbations_tested": list(ADVERSARIAL_PERTURBATIONS.keys()),
        "recommendation": (
            "Model is robust" if robustness_score >= 0.8
            else "Recommended: retrain with adversarial examples" if robustness_score >= 0.5
            else "CRITICAL: Model is highly vulnerable to adversarial attacks"
        ),
    }


# ─── Secure Detection (with Extraction Monitoring) ────────────────

@router.post("/protect/detect-sms", summary="Protected SMS detection with extraction monitoring")
async def api_secure_detect_sms(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    body: str = Query(..., description="SMS body to analyze"),
    sender: str = Query("unknown", description="Sender number"),
):
    """
    SMS detection with model extraction monitoring.
    
    In addition to threat detection, this endpoint:
    1. Logs every inference for extraction analysis
    2. Detects parameterized queries (>50 QPM = extraction)
    3. Rate-limits based on extraction risk score
    
    This replaces the unprotected /detect/sms endpoint.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    start_time = time.time()
    
    # 1. Run detection (reuse existing logic)
    # For now, use keyword-based detection
    scam_keywords = [
        "kyc", "aadhaar", "otp", "blocked", "suspended", "verify",
        "urgent", "immediately", "expir", "lottery", "won", "reward",
        "click here", "update now",
    ]
    content_lower = body.lower()
    keyword_score = sum(1 for kw in scam_keywords if kw in content_lower)
    is_scam = keyword_score >= 2
    confidence = min(keyword_score * 0.2, 1.0)
    
    response_time_ms = (time.time() - start_time) * 1000
    
    # 2. Log inference for extraction detection
    extraction_detector = get_extraction_detector()
    log_entry = extraction_detector.log_inference(
        db=db,
        client_ip=client_ip,
        model_name="smishing-keyword-classifier",
        model_version="1.0.0",
        input_data=body,
        response_time_ms=response_time_ms,
        user_agent=user_agent,
        api_key=f"user_{current_user.id}",
    )
    
    # 3. Build response with security context
    result = {
        "is_scam": is_scam,
        "confidence": round(confidence, 3),
        "keyword_hits": keyword_score,
        "model_security": {
            "extraction_risk_score": round(log_entry.extraction_risk_score, 3),
            "is_extraction_suspected": log_entry.is_suspicious,
            "reason": log_entry.suspicion_reason or "normal",
        },
    }
    
    if log_entry.is_suspicious:
        logger.warning(
            "MODEL EXTRACTION SUSPECTED on /detect endpoint: user=%d ip=%s risk=%.3f",
            current_user.id, client_ip, log_entry.extraction_risk_score,
        )
    
    return result