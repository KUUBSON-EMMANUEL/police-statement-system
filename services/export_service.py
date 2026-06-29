"""
Export services: generate PDF statement reports and CSV exports of
search results.
"""

import csv
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def statement_to_pdf(statement, case, officer):
    """Render a single statement as a printable PDF and return raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=16, spaceAfter=4
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading3"], spaceBefore=12, spaceAfter=6,
        textColor=colors.HexColor("#1a3c6e"),
    )
    body_style = styles["BodyText"]

    elements = []
    elements.append(Paragraph("OFFICIAL POLICE STATEMENT RECORD", title_style))
    elements.append(Paragraph(f"Statement ID: {statement.statement_id}", body_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Case info table
    elements.append(Paragraph("Case Information", heading_style))
    case_data = [
        ["Case Number", case.case_number, "Case Type", case.case_type],
        ["Date Reported", str(case.date_reported), "Station", case.station_name],
    ]
    case_table = Table(case_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
    case_table.setStyle(_table_style())
    elements.append(case_table)

    # Officer info
    elements.append(Paragraph("Recording Officer", heading_style))
    officer_data = [
        ["Officer Name", officer.full_name, "Rank", officer.rank or "-"],
        ["Officer ID", officer.officer_id or "-", "Username", officer.username],
    ]
    officer_table = Table(officer_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
    officer_table.setStyle(_table_style())
    elements.append(officer_table)

    # Person info
    elements.append(Paragraph("Person Giving Statement", heading_style))
    person_data = [
        ["Full Name", statement.person_name, "Gender", statement.gender or "-"],
        ["Date of Birth", str(statement.dob) if statement.dob else "-", "National ID", statement.national_id or "-"],
        ["Occupation", statement.occupation or "-", "Phone", statement.phone or "-"],
        ["Address", statement.address or "-", "", ""],
    ]
    person_table = Table(person_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
    person_table.setStyle(_table_style())
    elements.append(person_table)

    # Statement details
    elements.append(Paragraph("Statement Details", heading_style))
    elements.append(Paragraph(
        f"<b>Type:</b> {statement.statement_type} &nbsp;&nbsp; "
        f"<b>Date:</b> {statement.statement_date} &nbsp;&nbsp; "
        f"<b>Time:</b> {statement.statement_time}",
        body_style,
    ))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("<b>Statement:</b>", body_style))
    elements.append(Paragraph(statement.statement_text.replace("\n", "<br/>"), body_style))

    if statement.evidence:
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph("<b>Evidence Description:</b>", body_style))
        elements.append(Paragraph(statement.evidence.replace("\n", "<br/>"), body_style))

    if statement.notes:
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph("<b>Additional Notes:</b>", body_style))
        elements.append(Paragraph(statement.notes.replace("\n", "<br/>"), body_style))

    elements.append(Spacer(1, 1.5 * cm))
    elements.append(Paragraph("____________________________", body_style))
    elements.append(Paragraph("Officer's Signature", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def _table_style():
    return TableStyle(
        [
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )


def statements_to_csv(statements):
    """Export a list of Statement objects (with .case and .officer loaded) to CSV bytes."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Statement ID",
            "Case Number",
            "Case Type",
            "Officer",
            "Person Name",
            "Statement Type",
            "Statement Date",
            "Statement Time",
            "National ID",
            "Phone",
        ]
    )
    for s in statements:
        writer.writerow(
            [
                s.statement_id,
                s.case.case_number if s.case else "",
                s.case.case_type if s.case else "",
                s.officer.full_name if s.officer else "",
                s.person_name,
                s.statement_type,
                s.statement_date,
                s.statement_time,
                s.national_id or "",
                s.phone or "",
            ]
        )
    return output.getvalue().encode("utf-8")
