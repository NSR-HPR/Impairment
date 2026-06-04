#!/usr/bin/env python3
"""
NSR Sprinkler System Impairment Notification PDF Generator
Replace the sample_data dict values with Zapier data pills when deploying.
"""

import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.colors import HexColor

# ── Brand colors ──────────────────────────────────────────────────────────────
NSR_RED    = HexColor("#C0392B")
NSR_DARK   = HexColor("#1A1A2E")
NSR_MID    = HexColor("#2C3E50")
NSR_LIGHT  = HexColor("#ECF0F1")
NSR_ACCENT = HexColor("#E8F4F8")
NSR_BORDER = HexColor("#BDC3C7")
NSR_LABEL  = HexColor("#7F8C8D")
WHITE      = colors.white

def build_pdf(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.65*inch,
        rightMargin=0.65*inch,
        topMargin=0.55*inch,
        bottomMargin=0.6*inch,
        title="NSR Impairment Notification",
        author="National Safety & Risk",
    )

    content_width = letter[0] - 1.3*inch
    story = []

    # ── Styles ────────────────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    def style(name, **kw):
        s = ParagraphStyle(name, **kw)
        return s

    hdr_title = style("HdrTitle",
        fontName="Helvetica-Bold", fontSize=15, textColor=WHITE,
        leading=19, alignment=TA_LEFT)
    hdr_sub = style("HdrSub",
        fontName="Helvetica", fontSize=8.5, textColor=HexColor("#F0F0F0"),
        leading=12, alignment=TA_LEFT)
    hdr_date = style("HdrDate",
        fontName="Helvetica", fontSize=8, textColor=HexColor("#F0F0F0"),
        leading=11, alignment=TA_RIGHT)

    sec_heading = style("SecHeading",
        fontName="Helvetica-Bold", fontSize=9, textColor=WHITE,
        leading=12, alignment=TA_LEFT)
    sec_num = style("SecNum",
        fontName="Helvetica-Bold", fontSize=7.5, textColor=HexColor("#FFCCCC"),
        leading=10, alignment=TA_LEFT)

    label_style = style("Label",
        fontName="Helvetica-Bold", fontSize=8, textColor=NSR_LABEL,
        leading=11)
    value_style = style("Value",
        fontName="Helvetica", fontSize=9, textColor=NSR_DARK,
        leading=12)
    value_bold = style("ValueBold",
        fontName="Helvetica-Bold", fontSize=9, textColor=NSR_DARK,
        leading=12)
    desc_style = style("Desc",
        fontName="Helvetica", fontSize=8.5, textColor=NSR_MID,
        leading=12)
    footer_style = style("Footer",
        fontName="Helvetica", fontSize=7, textColor=NSR_LABEL,
        leading=10, alignment=TA_CENTER)
    notice_style = style("Notice",
        fontName="Helvetica-Oblique", fontSize=7.5, textColor=NSR_LABEL,
        leading=11)

    submitted_dt = data.get("submitted_at", datetime.now().strftime("%B %d, %Y at %I:%M %p"))

    # ── HEADER ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("NATIONAL SAFETY &amp; RISK<br/><font size='9'>Sprinkler System Impairment Notification</font>", hdr_title),
        Paragraph(f"Submitted<br/>{submitted_dt}", hdr_date)
    ]]
    header_table = Table(header_data, colWidths=[content_width * 0.68, content_width * 0.32])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NSR_RED),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (0,0), 14),
        ("RIGHTPADDING",(-1,0),(-1,0), 12),
        ("TOPPADDING",  (0,0), (-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("ROUNDEDCORNERS", [4,4,0,0]),
    ]))
    story.append(header_table)

    # Submission banner
    banner_data = [[
        Paragraph("IMPAIRMENT NOTIFICATION SUMMARY", style("BannerL",
            fontName="Helvetica-Bold", fontSize=8, textColor=NSR_MID, leading=10)),
        Paragraph(f"Form submitted: {submitted_dt}", style("BannerR",
            fontName="Helvetica", fontSize=8, textColor=NSR_LABEL, leading=10, alignment=TA_RIGHT))
    ]]
    banner = Table(banner_data, colWidths=[content_width*0.6, content_width*0.4])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NSR_ACCENT),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (0,0), 12),
        ("RIGHTPADDING",  (-1,0),(-1,0), 12),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, NSR_BORDER),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))

    # ── Helper: section header ─────────────────────────────────────────────────
    def section_header(num, title):
        row = [[
            Paragraph(num, sec_num),
            Paragraph(title, sec_heading)
        ]]
        t = Table(row, colWidths=[38, content_width - 38])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), NSR_MID),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (0,0), 10),
            ("LEFTPADDING",   (1,0), (1,0), 4),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        return t

    # ── Helper: two-column field rows ─────────────────────────────────────────
    def field_row(label1, val1, label2=None, val2=None, col_widths=None):
        if col_widths is None:
            col_widths = [content_width*0.22, content_width*0.28,
                          content_width*0.22, content_width*0.28]
        if label2 is None:
            # Full-width single field
            cw = [content_width*0.22, content_width*0.78]
            row = [[Paragraph(label1, label_style), Paragraph(str(val1), value_style)]]
            t = Table(row, colWidths=cw)
        else:
            row = [[
                Paragraph(label1, label_style), Paragraph(str(val1), value_style),
                Paragraph(label2, label_style), Paragraph(str(val2 or "—"), value_style)
            ]]
            t = Table(row, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1), NSR_LIGHT),
            ("BACKGROUND",    (2,0), (2,-1), NSR_LIGHT),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("LINEBELOW",     (0,0), (-1,-1), 0.5, NSR_BORDER),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        return t

    # ── SECTION 1: Customer & Property ───────────────────────────────────────
    story.append(KeepTogether([
        section_header("SEC. 01", "Customer &amp; Property Information"),
        Spacer(1, 2),
        field_row("CUSTOMER / COMPANY",   data["customer_name"],
                  "PROPERTY / FACILITY",  data["property_name"]),
        field_row("PROPERTY ADDRESS",     data["property_address"]),
        field_row("ON-SITE CONTACT",      data["contact_name"],
                  "CONTACT TITLE",        data["contact_title"]),
        field_row("CONTACT EMAIL",        data["contact_email"],
                  "CONTACT PHONE",        data["contact_phone"]),
        field_row("ALTERNATE CONTACT",    data.get("alt_contact_name", "—"),
                  "ALTERNATE PHONE",      data.get("alt_contact_phone", "—")),
        Spacer(1, 10),
    ]))

    # ── SECTION 2: Impairment Details ────────────────────────────────────────
    story.append(KeepTogether([
        section_header("SEC. 02", "Impairment Classification &amp; Details"),
        Spacer(1, 2),
        field_row("IMPAIRMENT TYPE",      data["impairment_type"],
                  "SYSTEM / ZONE",        data["system_affected"]),
        field_row("AREA / LOCATION",      data["area_affected"],
                  "HEADS AFFECTED",       data.get("heads_affected", "—")),
        field_row("REASON",               data["reason_for_impairment"]),
        field_row("IMPAIRMENT START",     data["impairment_start"],
                  "EST. RESTORATION",     data["estimated_restoration"]),
        Spacer(1, 4),
    ]))

    # Description box
    if data.get("impairment_description"):
        desc_data = [[
            Paragraph("DESCRIPTION OF IMPAIRMENT", label_style),
        ],[
            Paragraph(data["impairment_description"], desc_style),
        ]]
        desc_table = Table(desc_data, colWidths=[content_width])
        desc_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), NSR_LIGHT),
            ("BACKGROUND",    (0,1), (-1,1), WHITE),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("BOX",           (0,0), (-1,-1), 0.5, NSR_BORDER),
            ("LINEBELOW",     (0,0), (-1,0), 0.5, NSR_BORDER),
        ]))
        story.append(desc_table)

    story.append(Spacer(1, 10))

    # ── SECTION 3: Coordinator & Contractor ──────────────────────────────────
    story.append(KeepTogether([
        section_header("SEC. 03", "Impairment Coordinator &amp; Contractor"),
        Spacer(1, 2),
        field_row("COORDINATOR NAME",     data["coordinator_name"],
                  "COORDINATOR PHONE",    data["coordinator_phone"]),
        field_row("CONTRACTOR COMPANY",   data.get("contractor_company", "—"),
                  "LICENSE NO.",          data.get("contractor_license", "—")),
        field_row("CONTRACTOR CONTACT",   data.get("contractor_contact", "—"),
                  "CONTRACTOR PHONE",     data.get("contractor_phone", "—")),
        Spacer(1, 10),
    ]))

    # ── SECTION 4: Notifications & Fire Watch ────────────────────────────────
    checkboxes = [
        ("fire_dept_notified",       "Fire Department Notified"),
        ("insurance_notified",       "Insurance Carrier Notified"),
        ("alarm_company_notified",   "Alarm / Monitoring Company Notified"),
        ("occupants_notified",       "Building Occupants Notified"),
        ("fire_watch_established",   "Fire Watch Established"),
        ("hot_work_suspended",       "Hot Work Suspended in Impaired Area"),
        ("temp_protection_provided", "Temporary Protection / Extinguishers Provided"),
    ]

    cb_rows = []
    for key, label in checkboxes:
        checked = data.get(key, False)
        mark = "✓" if checked else "○"
        mark_color = HexColor("#27AE60") if checked else NSR_LABEL
        cb_rows.append([
            Paragraph(f'<font color="{mark_color.hexval()}" size="11"><b>{mark}</b></font>',
                      style(f"CB_{key}", fontName="Helvetica-Bold", fontSize=10,
                            textColor=mark_color, leading=13, alignment=TA_CENTER)),
            Paragraph(label, style(f"CBL_{key}", fontName="Helvetica", fontSize=9,
                                   textColor=NSR_DARK if checked else NSR_LABEL,
                                   leading=12))
        ])

    cb_table = Table(cb_rows, colWidths=[28, content_width - 28])
    cb_style = [
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (0,-1), 6),
        ("LEFTPADDING",   (1,0), (1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",     (0,0), (-1,-1), 0.3, NSR_BORDER),
    ]
    for i in range(0, len(cb_rows), 2):
        cb_style.append(("BACKGROUND", (0,i), (-1,i), NSR_ACCENT))
    cb_table.setStyle(TableStyle(cb_style))

    story.append(KeepTogether([
        section_header("SEC. 04", "Notifications &amp; Fire Watch Precautions"),
        Spacer(1, 2),
        cb_table,
        Spacer(1, 10),
    ]))

    # ── ACKNOWLEDGMENT ───────────────────────────────────────────────────────
    ack_data = [[
        Paragraph("Submitted By (Customer)<br/><font size='7' color='#7F8C8D'>"
                  "Signature / Date</font>", style("AckL",
                  fontName="Helvetica", fontSize=9, textColor=NSR_MID, leading=13)),
    ]]
    ack_table = Table(ack_data, colWidths=[content_width*0.5])
    ack_table.setStyle(TableStyle([
        ("BOX",           (0,0), (0,0), 0.5, NSR_BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("BACKGROUND",    (0,0), (0,0), NSR_ACCENT),
    ]))
    story.append(ack_table)
    story.append(Spacer(1, 10))

    # ── FOOTER NOTICE ────────────────────────────────────────────────────────
    story.append(HRFlowable(width=content_width, thickness=0.5, color=NSR_BORDER))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "This document was automatically generated by the NSR Impairment Notification System upon form submission. "
        "It serves as an official record of the impairment notification for National Safety &amp; Risk. "
        "Please retain this document for your records.",
        notice_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "National Safety &amp; Risk  |  NSR Impairment Management Program  |  pnephin@natsr.com",
        footer_style))

    doc.build(story)
    print(f"✅  PDF saved to: {output_path}")


# ── Sample data (replace with Zapier data pills) ─────────────────────────────
sample_data = {
    # Section 1
    "customer_name":        "Acme Corporation",
    "property_name":        "Acme Warehouse — Building C",
    "property_address":     "123 Main Street, Lancaster, PA 17601",
    "contact_name":         "John Smith",
    "contact_title":        "Facilities Manager",
    "contact_email":        "jsmith@acmecorp.com",
    "contact_phone":        "(717) 555-0142",
    "alt_contact_name":     "Sarah Johnson",
    "alt_contact_phone":    "(717) 555-0199",
    # Section 2
    "impairment_type":      "Planned",
    "system_affected":      "Zone 3 — West Wing",
    "area_affected":        "Warehouse floor, bays 12–18",
    "heads_affected":       "24",
    "reason_for_impairment":"Annual Inspection / Testing",
    "impairment_start":     "June 3, 2026 at 8:00 AM",
    "estimated_restoration":"June 3, 2026 at 5:00 PM",
    "impairment_description":
        "Annual inspection and flow testing of Zone 3 wet-pipe system. "
        "Main control valve will be closed for the duration. "
        "Contractor will perform 2-inch drain test and inspector's test valve verification.",
    # Section 3
    "coordinator_name":     "John Smith",
    "coordinator_phone":    "(717) 555-0142",
    "contractor_company":   "PA Fire Protection Services LLC",
    "contractor_license":   "PA-FP-00412",
    "contractor_contact":   "Mike Torres",
    "contractor_phone":     "(717) 555-0177",
    # Section 4 checkboxes
    "fire_dept_notified":       True,
    "insurance_notified":       True,
    "alarm_company_notified":   True,
    "occupants_notified":       True,
    "fire_watch_established":   True,
    "hot_work_suspended":       False,
    "temp_protection_provided": True,
    # Meta
    "submitted_at": "June 3, 2026 at 12:36 PM",
}

if __name__ == "__main__":
    import json as _json
    if len(sys.argv) == 3:
        # Called from Netlify function: generate_nsr_pdf.py <data.json> <out.pdf>
        with open(sys.argv[1]) as f:
            data = _json.load(f)
        build_pdf(data, sys.argv[2])
    else:
        # Standalone test with sample data
        out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/NSR-Impairment-Notification.pdf"
        build_pdf(sample_data, out)
