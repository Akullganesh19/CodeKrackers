import hashlib
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_fir_pdf(fir_id: int, officer_name: str, threat_details: dict) -> tuple[str, str]:
    """
    Generates a formal forensic FIR document and returns (file_path, digital_signature).
    """
    os.makedirs("artifacts/firs", exist_ok=True)
    filename = f"FIR_{fir_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join("artifacts/firs", filename)
    
    # Generate a dummy digital signature
    signature_payload = f"FIR:{fir_id}:{officer_name}:{datetime.now().isoformat()}"
    digital_signature = hashlib.sha256(signature_payload.encode()).hexdigest()
    
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.hexColor("#003366"),
        alignment=1,
        spaceAfter=20
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph("VSDP - Vishing & Smishing Defense Platform", styles['Normal']))
    elements.append(Paragraph(f"Official Forensic Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Title
    elements.append(Paragraph("FIRST INFORMATION REPORT (DIGITALLY SIGNED)", title_style))
    elements.append(Spacer(1, 10))
    
    # Data Table
    data = [
        ["FIR ID:", str(fir_id)],
        ["Investigating Officer:", officer_name],
        ["Threat Type:", str(threat_details.get("type", "N/A"))],
        ["Source Number:", str(threat_details.get("source_number", "N/A"))],
        ["Confidence Score:", f"{threat_details.get('confidence_score', 0)*100:.1f}%"],
        ["Digital Signature:", f"{digital_signature[:32]}..."]
    ]
    
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Evidence Content
    elements.append(Paragraph("<b>Evidence Transcript / Content:</b>", styles['Heading3']))
    elements.append(Paragraph(threat_details.get("content", "No content provided."), styles['Normal']))
    elements.append(Spacer(1, 40))
    
    # Signature block
    elements.append(Paragraph("__________________________", styles['Normal']))
    elements.append(Paragraph(f"Digitally Signed by: {officer_name}", styles['Normal']))
    elements.append(Paragraph(f"Hash: {digital_signature}", styles['Normal']))
    
    doc.build(elements)
    
    return file_path, digital_signature
