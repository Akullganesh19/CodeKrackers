from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
from ..core.database import get_db
from ..services.generator import generate_fir_pipeline
from pydantic import BaseModel
from ..models.orm import FIR

router = APIRouter(tags=["FIR Management"])


class FIRRequest(BaseModel):
    threat_id: uuid.UUID


@router.post("/generate")
async def generate_fir_endpoint(
    request: FIRRequest, db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to trigger the automated FIR generation pipeline for a specific threat.
    """
    try:
        fir_record = await generate_fir_pipeline(db, request.threat_id)
        return {
            "success": True,
            "fir_id": fir_record.id,
            "case_number": fir_record.case_number,
            "pdf_url": fir_record.pdf_path,
            "status": fir_record.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate FIR: {str(e)}")


@router.get("/{fir_id}/pdf")
async def download_fir_pdf(fir_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieves and serves the generated FIR PDF file for download.
    """
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir_record = result.scalar_one_or_none()

    if not fir_record:
        raise HTTPException(status_code=404, detail="FIR record not found")

    if not fir_record.pdf_path or not os.path.exists(fir_record.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on server")

    return FileResponse(
        path=fir_record.pdf_path,
        filename=f"{fir_record.case_number}.pdf",
        media_type="application/pdf",
    )
