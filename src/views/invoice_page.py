"""Streamlit invoice page.

The view wires user input to the calculator and PDF-builder controllers. It
holds no money math of its own: totals come from
:func:`src.controllers.calculator.compute_summary`.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from src import config
from src.controllers import build_invoice_pdf, compute_summary, subtotal_of
from src.models import Client, Company, Invoice, InvoiceItem, PaymentAccount
from src.views.styles import PAGE_CSS


def _init_state() -> None:
    if "invoice_items" not in st.session_state:
        st.session_state.invoice_items = []
    if "invoice_number" not in st.session_state:
        st.session_state.invoice_number = (
            f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        )


def _company_sidebar() -> Company:
    defaults = config.default_company()
    with st.sidebar:
        st.markdown("### Company Information")
        name = st.text_input("Company Name", defaults["name"])
        address = st.text_area("Address", defaults["address"])
        phone = st.text_input("Phone", defaults["phone"])
        email = st.text_input("Email", defaults["email"])
        website = st.text_input("Website", defaults["website"])
    return Company(name=name, address=address, phone=phone, email=email, website=website)


def _client_section() -> Client:
    st.subheader("Client / Customer Information")
    st.info("Fill in the client details below to generate the invoice.")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Name *", "", placeholder="Enter client/customer name")
        phone = st.text_input("Client Phone", "", placeholder="+92-XXX-XXXXXXX")
    with col2:
        email = st.text_input("Client Email", "", placeholder="client@example.com")
        address = st.text_area("Client Address", "", placeholder="Enter complete address")

    return Client(name=name, address=address, phone=phone, email=email)


def _add_item_section() -> None:
    st.subheader("Add Items / Services")
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        item_name = st.text_input("Item/Service Description", key="item_name")
    with col2:
        item_qty = st.number_input("Quantity", min_value=1, value=1, key="item_qty")
    with col3:
        item_rate = st.number_input(
            f"Rate ({config.CURRENCY})", min_value=0.0, value=0.0, step=0.01, key="item_rate"
        )
    with col4:
        st.write("")
        st.write("")
        if st.button("Add Item"):
            if item_name and item_rate > 0:
                st.session_state.invoice_items.append(
                    InvoiceItem(
                        description=item_name, quantity=item_qty, rate=item_rate
                    ).as_dict()
                )
                st.success("Item added.")
                st.rerun()
            else:
                st.error("Please enter an item description and a rate.")


def _render_items_table() -> None:
    df = pd.DataFrame(st.session_state.invoice_items)
    display_df = df.copy()
    display_df["rate"] = display_df["rate"].apply(lambda x: f"{config.CURRENCY} {x:,.2f}")
    display_df["amount"] = display_df["amount"].apply(
        lambda x: f"{config.CURRENCY} {x:,.2f}"
    )
    display_df = display_df.rename(
        columns={
            "description": "Description",
            "quantity": "Quantity",
            "rate": "Rate",
            "amount": "Amount",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    _, col_del = st.columns([3, 1])
    with col_del:
        if st.button("Clear All Items"):
            st.session_state.invoice_items = []
            st.rerun()


def _summary_section():
    """Render the summary controls and return (summary, notes)."""
    subtotal = subtotal_of(st.session_state.invoice_items)

    st.subheader("Invoice Summary")
    st.write(f"**Subtotal:** {config.CURRENCY} {subtotal:,.2f}")

    discount_type = st.radio(
        "Discount Type",
        ["Percentage (%)", f"Fixed Amount ({config.CURRENCY})"],
        horizontal=True,
    )
    discount_is_percent = discount_type == "Percentage (%)"
    if discount_is_percent:
        discount_value = st.number_input(
            "Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1
        )
    else:
        discount_value = st.number_input(
            f"Discount Amount ({config.CURRENCY})",
            min_value=0.0,
            max_value=float(subtotal),
            value=0.0,
            step=0.01,
        )

    tax_percent = st.number_input(
        "Tax/GST (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1
    )

    summary = compute_summary(
        subtotal,
        discount_is_percent=discount_is_percent,
        discount_value=discount_value,
        tax_percent=tax_percent,
    )

    st.write(
        f"**Discount:** {config.CURRENCY} {summary.discount_amount:,.2f} "
        f"({summary.discount_percent:.1f}%)"
    )
    st.write(
        f"**Tax ({summary.tax_percent}%):** {config.CURRENCY} {summary.tax_amount:,.2f}"
    )
    st.markdown(f"### **Total: {config.CURRENCY} {summary.total:,.2f}**")

    notes = st.text_area("Additional Notes", "Thank you for your business!")
    return summary, notes


def _resolve_logo_path() -> str | None:
    path = config.LOGO_PATH
    if os.path.exists(path):
        return path
    fallback = os.path.basename(path)
    return fallback if os.path.exists(fallback) else None


def _generate_section(company, client, invoice_number, invoice_date, summary, notes):
    st.divider()
    _, col_mid, _ = st.columns(3)
    with col_mid:
        if st.button("Generate Invoice PDF", type="primary"):
            invoice = Invoice(
                number=invoice_number,
                date=invoice_date,
                company=company,
                client=client,
                items=[
                    InvoiceItem(
                        description=i["description"],
                        quantity=i["quantity"],
                        rate=i["rate"],
                    )
                    for i in st.session_state.invoice_items
                ],
                discount_amount=summary.discount_amount,
                tax_percent=summary.tax_percent,
                notes=notes,
                payment_accounts=[
                    PaymentAccount(**acc) for acc in config.payment_accounts()
                ],
            )
            pdf_buffer = build_invoice_pdf(invoice, _resolve_logo_path())
            st.download_button(
                label="Download Invoice PDF",
                data=pdf_buffer,
                file_name=(
                    f"Invoice_{invoice_number}_"
                    f"{datetime.now().strftime('%Y%m%d')}.pdf"
                ),
                mime="application/pdf",
            )
            st.success("Invoice generated successfully. Use the button above to download.")
            st.info("Tip: you can print the downloaded PDF directly from your PDF viewer.")


def render() -> None:
    """Render the full invoice generator page."""
    st.set_page_config(page_title=config.APP_TITLE, layout="wide")
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    _init_state()

    st.markdown(
        '<div class="invoice-header"><h1>Sairow Solutions Invoice Generator</h1></div>',
        unsafe_allow_html=True,
    )

    company = _company_sidebar()

    st.subheader("Invoice Details")
    col1, col2 = st.columns(2)
    with col1:
        invoice_number = st.text_input("Invoice Number", st.session_state.invoice_number)
    with col2:
        invoice_date = st.date_input("Invoice Date", datetime.now())

    st.divider()
    client = _client_section()
    st.divider()
    _add_item_section()

    summary = None
    notes = ""
    if st.session_state.invoice_items:
        st.subheader("Invoice Items")
        _render_items_table()
        st.divider()
        col_left, col_right = st.columns([2, 1])
        with col_right:
            summary, notes = _summary_section()

    if st.session_state.invoice_items and client.name and summary is not None:
        _generate_section(
            company, client, invoice_number, invoice_date, summary, notes
        )
    elif not st.session_state.invoice_items:
        st.info("Please add at least one item to generate an invoice.")
    elif not client.name:
        st.error(
            "Please enter the client name in the 'Client / Customer Information' "
            "section to generate the invoice."
        )

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>Powered by <b>Sairow Solutions</b> | www.sairowsolutionsgb.com</p>
            <p style='font-size: 0.8rem;'>Professional Invoice Generator</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
