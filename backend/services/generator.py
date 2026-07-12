import uuid
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Importing models from the application structure
from ..models.orm import FIR, Threat, User
from .ipc_tagger import tag_ipc_sections
from ..utils.pdf_builder import generate_fir_pdf


async def generate_fir_pipeline(db: AsyncSession, threat_id: uuid.UUID) -> FIR:
    """
    Executes the complete FIR generation pipeline:
    1. Data Collection: Fetches threat details and complainant (user) info.
    2. Legal Analysis: Auto-tags IPC/IT Act sections based on threat patterns.
    3. Identity Generation: Creates a unique Case Number (VSD-YYYY-XXXXX).
    4. Document Production: Builds a tamper-proof PDF FIR.
    5. Persistence: Stores the record and document path in the database.
    """

    # 1. Gather required data from Threat and User tables
    result = await db.execute(
        select(Threat, User)
        .join(User, Threat.user_id == User.id)
        .where(Threat.id == threat_id)
    )
    data = result.first()

    if not data:
        raise ValueError(f"Threat with ID {threat_id} or associated User not found.")

    threat, user = data

    # 2. Analyze threat for legal tagging
    # risk_factors in extra_info are used to determine specific offences (e.g. Identity Theft vs Cheating)
    risk_factors = (threat.extra_info or {}).get("risk_factors", [])
    ipc_tags = tag_ipc_sections(threat.type, risk_factors)

    # 3. Initialize the FIR record to obtain an ID
    new_fir = FIR(
        threat_id=threat.id,
        user_id=user.id,
        complainant=user.full_name or user.email,
        offence_type=str(threat.type),
        ipc_sections=ipc_tags,
        evidence_hash=threat.evidence_hash,
        scammer_details={
            "caller_id": threat.caller_id,
            "sender_id": threat.sender_id,
            "urls": threat.suspicious_urls,
        },
        status="draft",
    )

    db.add(new_fir)
    await db.flush()  # Populates new_fir.id (UUID)

    # 4. Generate Case Number: VSD-{Year}-{5-digit-padded-part}
    # Using a portion of the UUID integer for a unique numeric suffix
    case_id_part = str(new_fir.id.int)[:5].zfill(5)
    new_fir.case_number = f"VSD-{datetime.now().year}-{case_id_part}"

    # 5. Build PDF Document
    storage_dir = "storage/firs"
    os.makedirs(storage_dir, exist_ok=True)
    pdf_path = os.path.join(storage_dir, f"{new_fir.case_number}.pdf")

    # Prepare the payload for reportlab-based pdf_builder
    pdf_data = {
        "case_number": new_fir.case_number,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "complainant": new_fir.complainant,
        "offence_type": new_fir.offence_type.upper(),
        "ipc_sections": [tag["section"] for tag in ipc_tags],
        "raw_content": threat.raw_content or "No content captured",
        "evidence_hash": threat.evidence_hash or "NOT_Hashed",
    }

    # Trigger PDF Generation
    generate_fir_pdf(pdf_data, pdf_path)

    # 6. Finalize persistence
    new_fir.pdf_path = pdf_path
    await db.commit()

    return new_fir
