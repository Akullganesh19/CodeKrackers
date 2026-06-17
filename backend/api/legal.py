"""
Legal endpoints: FIR generation with digital signatures and chain of custody.
"""
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models import Evidence, FIR, FIRStatus, Threat, User, UserRole
from backend.schemas.legal import FIR as FIRSchema
from backend.utils.pdf import generate_fir_pdf

logger = logging.getLogger("vas.legal")
router = APIRouter()


@router.post("/generate-fir/{threat_id}", response_model=FIRSchema)
def create_fir(
    threat_id: int,
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Generate a digitally signed FIR draft for a specific threat."""
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    # RBAC: only owner, officers, or admins can generate FIR
    if threat.owner_id != current_user.id and current_user.role not in {
        UserRole.ADMIN, UserRole.OFFICER, UserRole.SUPER_ADMIN
    }:
        raise HTTPException(status_code=403, detail="Not authorized to report this threat")

    # Idempotency: return existing FIR if already generated
    existing_fir = db.query(FIR).filter(FIR.threat_id == threat_id).first()
    if existing_fir:
        logger.info("FIR_EXISTS threat_id=%d fir_id=%d", threat_id, existing_fir.id)
        return existing_fir

    # Create FIR record
    fir = FIR(
        reporter_id=current_user.id,
        threat_id=threat_id,
        status=FIRStatus.DRAFT,
        legal_sections="IPC §420, IT Act §66C, IT Act §66D",
    )
    db.add(fir)
    db.commit()
    db.refresh(fir)

    # Generate digitally signed PDF
    threat_details = {
        "type": threat.type.value if hasattr(threat.type, 'value') else threat.type,
        "source_number": threat.source_number,
        "content": threat.content,
        "confidence_score": threat.confidence_score,
    }

    try:
        pdf_path, signature = generate_fir_pdf(fir.id, current_user.full_name, threat_details)
        fir.fir_copy_path = pdf_path
    except Exception as e:
        logger.error("PDF_GENERATION_FAILED fir_id=%d: %s", fir.id, e)
        pdf_path, signature = None, "pdf-generation-failed"

    # Create Evidence anchoring
    evidence = Evidence(
        threat_id=threat_id,
        digital_signature=signature,
        evidence_package_path=pdf_path or "",
        blockchain_hash=signature,
        collected_by=current_user.full_name,
    )
    db.add(evidence)
    db.commit()
    db.refresh(fir)

    logger.info(
        "FIR_GENERATED id=%d threat=%d reporter=%d signature=%s",
        fir.id, threat_id, current_user.id, signature[:16] + "...",
    )
    return fir


@router.get("/firs", response_model=List[FIRSchema])
def read_firs(
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve FIRs with RBAC filtering."""
    if current_user.role in {UserRole.ADMIN, UserRole.OFFICER, UserRole.SUPER_ADMIN}:
        return db.query(FIR).order_by(FIR.created_at.desc()).all()
    return db.query(FIR).filter(FIR.reporter_id == current_user.id).order_by(FIR.created_at.desc()).all()


@router.patch("/firs/{fir_id}/status")
def update_fir_status(
    fir_id: int,
    body: dict,
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_officer_or_admin),
) -> Any:
    """Update FIR status (officers/admins only)."""
    fir = db.query(FIR).filter(FIR.id == fir_id).first()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    new_status = body.get("status")
    try:
        fir.status = FIRStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {[s.value for s in FIRStatus]}",
        )

    db.commit()
    logger.info("FIR_STATUS_UPDATED id=%d status=%s by=%d", fir_id, new_status, current_user.id)
    return {"id": fir_id, "status": fir.status}
