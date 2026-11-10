"""Invoice calculations.

Pure functions with no Streamlit or PDF dependencies so the money math can be
reasoned about (and tested) in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass
class InvoiceSummary:
    """Computed totals for an invoice."""

    subtotal: float
    discount_amount: float
    discount_percent: float
    tax_percent: float
    tax_amount: float
    total: float


def subtotal_of(items: Iterable[Mapping]) -> float:
    """Sum the ``amount`` (quantity * rate) of each item."""
    return sum(float(item["quantity"]) * float(item["rate"]) for item in items)


def compute_summary(
    subtotal: float,
    *,
    discount_is_percent: bool,
    discount_value: float,
    tax_percent: float,
) -> InvoiceSummary:
    """Compute discount, tax, and grand total from a subtotal.

    ``discount_value`` is interpreted as a percentage when
    ``discount_is_percent`` is true, otherwise as a fixed amount.
    """
    subtotal = max(float(subtotal), 0.0)

    if discount_is_percent:
        discount_percent = float(discount_value)
        discount_amount = subtotal * discount_percent / 100
    else:
        discount_amount = min(float(discount_value), subtotal)
        discount_percent = (discount_amount / subtotal * 100) if subtotal > 0 else 0.0

    taxable = max(subtotal - discount_amount, 0.0)
    tax_amount = taxable * float(tax_percent) / 100
    total = subtotal - discount_amount + tax_amount

    return InvoiceSummary(
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_percent=discount_percent,
        tax_percent=float(tax_percent),
        tax_amount=tax_amount,
        total=total,
    )
