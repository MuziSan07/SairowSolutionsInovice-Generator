"""PDF generation for invoices.

Renders an :class:`~src.models.invoice.Invoice` into a print-ready PDF using
ReportLab and returns it as an in-memory buffer.
"""

from __future__ import annotations

import io
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import CURRENCY, PRIMARY_COLOR
from src.models import Invoice

_PRIMARY = colors.HexColor(PRIMARY_COLOR)


def _money(value: float) -> str:
    return f"{CURRENCY} {value:,.2f}"


def build_invoice_pdf(invoice: Invoice, logo_path: str | None = None) -> io.BytesIO:
    """Build the invoice PDF and return it as a seekable byte buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=_PRIMARY,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        alignment=TA_CENTER,
    )

    # Logo
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=80, height=80)
            img.hAlign = "CENTER"
            elements.append(img)
            elements.append(Spacer(1, 10))
        except Exception:
            # A broken or unsupported logo file must never block invoice output.
            pass

    # Company header
    company = invoice.company
    elements.append(Paragraph(company.name, title_style))
    elements.append(Paragraph(company.address, header_style))
    elements.append(
        Paragraph(f"Phone: {company.phone} | Email: {company.email}", header_style)
    )
    elements.append(Paragraph(f"Website: {company.website}", header_style))
    elements.append(Spacer(1, 20))

    # Invoice title
    invoice_title = ParagraphStyle(
        "InvoiceTitle", parent=styles["Heading2"], fontSize=18, textColor=_PRIMARY
    )
    elements.append(Paragraph("INVOICE", invoice_title))
    elements.append(Spacer(1, 20))

    # Invoice and client details
    client = invoice.client
    info_data = [
        ["Invoice Number:", invoice.number, "Bill To:", client.name],
        ["Invoice Date:", invoice.date.strftime("%B %d, %Y"), "Address:", client.address],
        ["", "", "Phone:", client.phone],
        ["", "", "Email:", client.email],
    ]
    info_table = Table(info_data, colWidths=[1.5 * inch, 2 * inch, 1 * inch, 2.5 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), _PRIMARY),
                ("TEXTCOLOR", (2, 0), (2, -1), _PRIMARY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 30))

    # Line items
    table_data = [["Description", "Quantity", f"Rate ({CURRENCY})", f"Amount ({CURRENCY})"]]
    for item in invoice.items:
        table_data.append(
            [
                item.description,
                str(item.quantity),
                f"{item.rate:,.2f}",
                f"{item.amount:,.2f}",
            ]
        )
    item_table = Table(
        table_data, colWidths=[3.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
    )
    item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
            ]
        )
    )
    elements.append(item_table)
    elements.append(Spacer(1, 20))

    # Summary
    summary_data = [
        ["Subtotal:", _money(invoice.subtotal)],
        ["Discount:", _money(invoice.discount_amount)],
        ["Tax:", _money(invoice.tax_amount)],
        ["Total:", _money(invoice.total)],
    ]
    summary_table = Table(summary_data, colWidths=[5.5 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("TEXTCOLOR", (0, -1), (-1, -1), _PRIMARY),
                ("LINEABOVE", (0, -1), (-1, -1), 2, _PRIMARY),
                ("FONTSIZE", (0, 0), (-1, -2), 10),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Notes
    if invoice.notes:
        elements.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", styles["Normal"]))
        elements.append(Spacer(1, 20))

    # Payment information (only when configured)
    if invoice.payment_accounts:
        elements.append(Spacer(1, 10))
        bank_title_style = ParagraphStyle(
            "BankTitle",
            parent=styles["Heading3"],
            fontSize=14,
            textColor=_PRIMARY,
            spaceAfter=10,
            fontName="Helvetica-Bold",
        )
        elements.append(Paragraph("Payment Information", bank_title_style))

        bank_data = [["Account Holder", "Payment Method", "Account Details"]]
        for account in invoice.payment_accounts:
            bank_data.append([account.account_holder, account.method, account.details])

        bank_table = Table(bank_data, colWidths=[2.2 * inch, 2 * inch, 3.3 * inch])
        bank_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(bank_table)
        elements.append(Spacer(1, 20))

    # Footer
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    elements.append(
        Paragraph(
            "Thank you for your business! For any queries, please contact us.",
            footer_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
