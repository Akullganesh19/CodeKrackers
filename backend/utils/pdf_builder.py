from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

def generate_fir_pdf(data: dict, output_path: str):
    """
    Generates a formal forensic FIR document using ReportLab.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
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

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=2
    )

    content = []

    # Header
    content.append(Paragraph("VSDP - Vishing & Smishing Defense Platform", header_style))
    content.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", header_style))
    content.append(Spacer(1, 20))

    # Title
    content.append(Paragraph("FIRST INFORMATION REPORT (FORENSIC)", title_style))
    content.append(Spacer(1, 10))

    # Basic Info Table
    info_data = [
        ["Case Number:", data.get("case_number", "N/A")],
        ["Date of Incident:", data.get("date", "N/A")],
        ["Complainant:", data.get("complainant", "N/A")],
        ["Type of Offence:", data.get("offence_type", "N/A")],
        ["Digital Evidence Hash:", data.get("evidence_hash", "N/A")[:32] + "..."]
    ]

    t = Table(info_data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    content.append(t)
    content.append(Spacer(1, 20))

    # Legal Sections
    content.append(Paragraph("<b>Relevant Legal Sections (IPC/IT Act):</b>", styles['Heading3']))
    for section in data.get("ipc_sections", []):
        content.append(Paragraph(f"• {section}", styles['Normal']))
    content.append(Spacer(1, 20))

    # Incident Details
    content.append(Paragraph("<b>Incident Description / Raw Evidence:</b>", styles['Heading3']))
    content.append(Paragraph(data.get("raw_content", "No content captured."), styles['Normal']))
    content.append(Spacer(1, 40))

    # Footer / Signature Placeholder
    content.append(Spacer(1, 40))
    content.append(Paragraph("__________________________", styles['Normal']))
    content.append(Paragraph("Authorized Digital Signature", styles['Normal']))
    content.append(Paragraph("VSDP Cyber Forensic Division", styles['Normal']))

    doc.build(content)
