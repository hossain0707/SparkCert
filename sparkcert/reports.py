"""PDF generation with transparent scope and reproducible evidence."""
from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

NAVY = colors.HexColor("#10263B")
TEAL = colors.HexColor("#087F71")
GRAY = colors.HexColor("#536577")


def pdf_bytes(run: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(595.28, 841.89),
                            leftMargin=47, rightMargin=47, topMargin=49, bottomMargin=45,
                            title=f"SparkCert Evidence Report {run['id']}",
                            author="SparkCert")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=NAVY))
    styles.add(ParagraphStyle(name="Subline", fontSize=10, leading=15, textColor=GRAY))
    styles.add(ParagraphStyle(name="Sec", fontName="Helvetica-Bold", fontSize=12, leading=17, spaceBefore=16, spaceAfter=7, textColor=NAVY))
    styles.add(ParagraphStyle(name="BodyCustom", fontSize=9, leading=14, textColor=NAVY))
    styles.add(ParagraphStyle(name="SmallCustom", fontSize=8, leading=12, textColor=GRAY))
    safe = lambda value: escape(str(value if value is not None else "—"))
    body = [Paragraph("SparkCert <font color='#087F71'>/</font> Evidence Report", styles["Brand"]),
            Paragraph("AI deployment readiness assessment · Local-first evidence", styles["Subline"]), Spacer(1, 19)]
    result = run["result"]
    def cell(s): return Paragraph(safe(s), styles["BodyCustom"])
    rows = [[cell("Assessment"), cell(run["kind"].replace("_", " ").title())],
            [cell("Target"), cell(run.get("device_name") or result.get("model", "Unspecified"))],
            [cell("Created (UTC)"), cell(run["created_at"])],
            [cell("Result ID"), cell(run["id"])],
            [cell("Pass rate"), cell(f"{result['score']}%" if result.get("score") is not None else "N/A")]]
    tbl = Table(rows, colWidths=[148, 347], hAlign="LEFT")
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F5F7")),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#F0F5F7"), colors.white]),
                            ("VALIGN", (0,0), (-1,-1), "TOP"),
                            ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
                            ("LINEBELOW", (0,0), (-1,-1), .4, colors.HexColor("#E1E8ED"))]))
    body += [tbl, Paragraph("Assessment summary", styles["Sec"]),
             Paragraph(safe(result.get("summary", "")), styles["BodyCustom"]),
             Paragraph("Recorded checks", styles["Sec"])]
    checks = result.get("checks") or result.get("cases") or []
    for idx, item in enumerate(checks, 1):
        status = "PASS" if item.get("passed") else "FAIL"
        title = f"{idx:02d} · {safe(item.get('name', 'Check'))} — {status}"
        detail = safe(item.get("detail", ""))
        if item.get("error"):
            detail += " | Error: " + safe(item["error"])
        if item.get("latency_ms") is not None:
            detail += " | Latency: " + safe(item["latency_ms"]) + " ms"
        body.append(KeepTogether([Paragraph(title, styles["BodyCustom"]),
                                  Paragraph(detail, styles["SmallCustom"]), Spacer(1, 9)]))
    body += [Paragraph("Method and limitations", styles["Sec"]),
             Paragraph(safe(result.get("method", "Unspecified")), styles["BodyCustom"]),
             Spacer(1, 6), Paragraph(safe(result.get("scope", "")), styles["SmallCustom"]),
             Spacer(1, 14),
             Paragraph("This report records observed test outcomes only. It is not an NVIDIA endorsement, external audit, regulatory approval, or formal certification.", styles["SmallCustom"])]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E1E8ED"))
        canvas.line(47, 37, 548, 37)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(47, 25, "SparkCert · Independent assessment software")
        canvas.drawRightString(548, 25, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(body, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
