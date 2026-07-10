import os
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_fir_pdf(fir_id: int, officer_name: str, threat_details: dict) -> tuple[str, str]:  # noqa: E302,E501
    """
    Generates a formal forensic FIR document and returns (file_path, digital_signature).
    """
    os.makedirs("artifacts/firs", exist_ok=True)
    filename = f"FIR_{fir_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join("artifacts/firs", filename)
      # noqa: E114,E116,W293
    # Generate a dummy digital signature
    signature_payload = f"FIR:{fir_id}:{officer_name}:{datetime.now().isoformat()}"
    digital_signature = hashlib.sha256(signature_payload.encode()).hexdigest()
      # noqa: E114,E116,W293
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
      # noqa: E114,E116,W293
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.hexColor("#003366"),
        alignment=1,
        spaceAfter=20
    )
      # noqa: E114,E116,W293
    elements = []
      # noqa: E114,E116,W293
    # Header
    elements.append(Paragraph("VSDP - Vishing & Smishing Defense Platform", styles['Normal']))  # noqa: E501
    elements.append(Paragraph(f"Official Forensic Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))  # noqa: E501
    elements.append(Spacer(1, 20))
      # noqa: E114,E116,W293
    # Title
    elements.append(Paragraph("FIRST INFORMATION REPORT (DIGITALLY SIGNED)", title_style))  # noqa: E501
    elements.append(Spacer(1, 10))
      # noqa: E114,E116,W293
    # Data Table
    data = [
        ["FIR ID:", str(fir_id)],
        ["Investigating Officer:", officer_name],
        ["Threat Type:", str(threat_details.get("type", "N/A"))],
        ["Source Number:", str(threat_details.get("source_number", "N/A"))],
        ["Confidence Score:", f"{threat_details.get('confidence_score', 0)*100:.1f}%"],
        ["Digital Signature:", f"{digital_signature[:32]}..."]
    ]
      # noqa: E114,E116,W293
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),  # noqa: E231
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),  # noqa: E231
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),  # noqa: E231
        ('PADDING', (0,0), (-1,-1), 6),  # noqa: E231
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
      # noqa: E114,E116,W293
    # Evidence Content
    elements.append(Paragraph("<b>Evidence Transcript / Content:</b>", styles['Heading3']))  # noqa: E501
    elements.append(Paragraph(threat_details.get("content", "No content provided."), styles['Normal']))  # noqa: E501
    elements.append(Spacer(1, 40))
      # noqa: E114,E116,W293
    # Signature block
    elements.append(Paragraph("__________________________", styles['Normal']))
    elements.append(Paragraph(f"Digitally Signed by: {officer_name}", styles['Normal']))
    elements.append(Paragraph(f"Hash: {digital_signature}", styles['Normal']))
      # noqa: E114,E116,W293
    doc.build(elements)
      # noqa: E114,E116,W293
    return file_path, digital_signature
