from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from ..core.database import get_db
from ..core.dependencies import get_current_user, require_role
from ..services.evidence_chain import EvidenceChain
from ..tasks import verify_all_evidence_chains

router = APIRouter(prefix="/api/evidence", tags=["Evidence Ledger"])

@router.get("/{threat_id}/verify")  # noqa: E302
async def verify_threat_evidence(
    threat_id: uuid.UUID,   # noqa: W291
    db: AsyncSession = Depends(get_db),   # noqa: W291
    current_user = Depends(get_current_user)  # noqa: E251
):
    """
    Triggers an integrity check for the entire evidence chain of a specific threat.
    Re-computes all hashes and verifies digital signatures to ensure no tampering has occurred.  # noqa: E501
    """
    ledger = EvidenceChain(db)
    result = await ledger.verify_integrity(threat_id)
    return result

@router.get("/{threat_id}/report")  # noqa: E302
async def get_forensic_package(
    threat_id: uuid.UUID,   # noqa: W291
    db: AsyncSession = Depends(get_db),   # noqa: W291
    current_user = Depends(get_current_user)  # noqa: E251
):
    """
    Compiles and returns a full forensic report for a threat, including
    incident data, complainant info, FIR filing status, and the blockchain audit trail.
    """
    ledger = EvidenceChain(db)
    try:
        report = await ledger.package_evidence(threat_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compile evidence: {str(e)}")  # noqa: E501

@router.post("/audit")  # noqa: E302
async def trigger_system_audit(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(4))  # noqa: E251
):
    """
    Manually triggers a full system audit of all evidence chains across the platform.
    """
    return await verify_all_evidence_chains()  # noqa: W292
