"""Application configuration.

Values that are environment specific or sensitive (company contact details and,
in particular, payment account numbers) are read from Streamlit secrets first,
then from environment variables, and only then fall back to safe placeholders.

Never hard-code real bank account numbers in source control. Configure them in
``.streamlit/secrets.toml`` (which is git-ignored) using
``.streamlit/secrets.toml.example`` as a template.
"""

from __future__ import annotations

import os
from typing import Any, List

try:  # Streamlit is optional at import time (e.g. when running unit checks).
    import streamlit as st
except Exception:  # pragma: no cover - defensive, Streamlit always present at runtime.
    st = None  # type: ignore[assignment]


def _secret(key: str, default: str = "") -> str:
    """Return a configuration value from Streamlit secrets, env, or a default."""
    if st is not None:
        try:
            if key in st.secrets:
                return str(st.secrets[key])
        except Exception:
            # No secrets file configured; fall through to environment/default.
            pass
    return os.environ.get(key, default)


# --- Branding -----------------------------------------------------------------
PRIMARY_COLOR = "#2E86AB"
APP_TITLE = "Sairow Solutions - Invoice Generator"
CURRENCY = "PKR"
LOGO_PATH = _secret("INVOICE_LOGO_PATH", "assets/SairowSolutionsGB logo.jpg")


# --- Default company details --------------------------------------------------
# These are public business contact details and are safe to ship as defaults.
def default_company() -> dict:
    return {
        "name": _secret("COMPANY_NAME", "Sairow Solutions"),
        "address": _secret("COMPANY_ADDRESS", "Gilgit-Baltistan, Pakistan"),
        "phone": _secret("COMPANY_PHONE", "+92-XXX-XXXXXXX"),
        "email": _secret("COMPANY_EMAIL", "info@sairowsolutionsgb.com"),
        "website": _secret("COMPANY_WEBSITE", "www.sairowsolutionsgb.com"),
    }


# --- Payment accounts (sensitive) ---------------------------------------------
def payment_accounts() -> List[dict]:
    """Return configured payment accounts for the invoice footer.

    Expected format in ``.streamlit/secrets.toml``::

        [[payment_accounts]]
        account_holder = "Full Name"
        method = "Bank / Wallet name"
        details = "Account number or IBAN"

    Returns an empty list when nothing is configured, in which case the payment
    section is omitted from the generated invoice.
    """
    accounts: Any = []
    if st is not None:
        try:
            accounts = st.secrets.get("payment_accounts", [])
        except Exception:
            accounts = []

    normalised: List[dict] = []
    for entry in accounts or []:
        normalised.append(
            {
                "account_holder": str(entry.get("account_holder", "")),
                "method": str(entry.get("method", "")),
                "details": str(entry.get("details", "")),
            }
        )
    return normalised
