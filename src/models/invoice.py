"""Domain models for invoices.

These are plain data structures with light derived properties. All currency
calculations live in :mod:`src.controllers.calculator` so there is a single
source of truth for the numbers shown on screen and written to the PDF.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Company:
    """The business issuing the invoice."""

    name: str
    address: str
    phone: str
    email: str
    website: str


@dataclass
class Client:
    """The customer being billed."""

    name: str
    address: str = ""
    phone: str = ""
    email: str = ""


@dataclass
class InvoiceItem:
    """A single line item on the invoice."""

    description: str
    quantity: int
    rate: float

    @property
    def amount(self) -> float:
        return self.quantity * self.rate

    def as_dict(self) -> dict:
        return {
            "description": self.description,
            "quantity": self.quantity,
            "rate": self.rate,
            "amount": self.amount,
        }


@dataclass
class PaymentAccount:
    """A payment destination shown in the invoice footer."""

    account_holder: str
    method: str
    details: str


@dataclass
class Invoice:
    """A complete invoice ready to be rendered to PDF."""

    number: str
    date: date
    company: Company
    client: Client
    items: List[InvoiceItem] = field(default_factory=list)
    discount_amount: float = 0.0
    tax_percent: float = 0.0
    notes: str = ""
    payment_accounts: List[PaymentAccount] = field(default_factory=list)

    @property
    def subtotal(self) -> float:
        return sum(item.amount for item in self.items)

    @property
    def tax_amount(self) -> float:
        return (self.subtotal - self.discount_amount) * self.tax_percent / 100

    @property
    def total(self) -> float:
        return self.subtotal - self.discount_amount + self.tax_amount
