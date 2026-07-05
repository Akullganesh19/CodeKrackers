from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_admin_report_pdf(data: dict, output_path: str):
    """
    Forensic utility to generate a formatted PDF report for the Admin Dashboard.
    Aggregates statistical tables and trend data into a document suitable for executive review.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header and Metadata
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], alignment=1)
    elements.append(Paragraph("VSDP Platform - Admin Dashboard Report", header_style))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(f"Generated at: {data['generated_at']}", styles['Normal']))
    filter_info = data['stats']['filter_applied']
    elements.append(Paragraph(
        f"Filters Applied: Month={filter_info['month'] or 'All'}, Year={filter_info['year'] or 'All'}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Platform High-Level Statistics
    elements.append(Paragraph("Core Platform Metrics", styles['Heading2']))
    stats_data = [
        ["Metric", "Total Count"],
        ["Threats Detected", str(data['stats']['total_threats'])],
        ["FIRs Successfully Filed", str(data['stats']['total_firs_filed'])]
    ]
    t_stats = Table(stats_data, colWidths=[200, 100])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(t_stats)
    elements.append(Spacer(1, 20))

    # Threat Type Distribution
    elements.append(Paragraph("Threat Distribution by Category", styles['Heading3']))
    type_data = [["Threat Type", "Incidents"]] + [[t.capitalize(), str(c)]
                                                  for t, c in data['stats']['threats_by_type'].items()]
    t_type = Table(type_data, colWidths=[200, 100])
    t_type.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(t_type)
    elements.append(Spacer(1, 20))

    # Severity Matrix
    elements.append(Paragraph("Severity Matrix", styles['Heading3']))
    sev_data = [["Severity Level", "Count"]] + [[s.upper(), str(c)]
                                                for s, c in data['stats']['threats_by_severity'].items()]
    t_sev = Table(sev_data, colWidths=[200, 100])
    t_sev.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(t_sev)
    elements.append(Spacer(1, 20))

    # 7-Day Incumbency Trend
    elements.append(Paragraph("7-Day Operational Trend", styles['Heading3']))
    trend_data = [["Date", "New Threats Detected"]] + [[d['date'],
                                                        str(d['count'])] for d in data['visualization']['threat_trend_7d']]
    t_trend = Table(trend_data, colWidths=[200, 100])
    t_trend.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(t_trend)

    doc.build(elements)
