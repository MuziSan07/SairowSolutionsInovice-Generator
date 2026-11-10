# Sairow Solutions Invoice Generator

A Streamlit web application for creating professional, print-ready PDF invoices.
Enter company and client details, add line items, apply discounts and tax, and
download a formatted invoice complete with a payment-information section.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

---

## Features

- Company and client detail entry
- Unlimited invoice line items with quantity and rate
- Percentage or fixed-amount discounts
- Configurable tax / GST
- Live invoice summary (subtotal, discount, tax, total)
- One-click PDF generation with company logo and payment details
- Payment account details sourced from secrets, not hard-coded

---

## Tech stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| PDF generation | ReportLab |
| Data handling | pandas |
| Images | Pillow |

---

## Project structure

The code follows a Model-View-Controller layout:

```
SairowSolutionsInovice-Generator/
├── app.py                      # Entry point (streamlit run app.py)
├── src/
│   ├── config.py               # Settings; reads secrets / env with safe defaults
│   ├── models/
│   │   └── invoice.py          # Company, Client, InvoiceItem, Invoice, PaymentAccount
│   ├── controllers/
│   │   ├── calculator.py       # Subtotal, discount, tax, total (pure functions)
│   │   └── pdf_builder.py      # Renders an Invoice to a PDF buffer
│   └── views/
│       ├── styles.py           # Page CSS
│       └── invoice_page.py     # Streamlit UI and orchestration
├── assets/                     # Company logo
├── .streamlit/
│   └── secrets.toml.example    # Template for company and payment configuration
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Prerequisites

- Python 3.9 or newer
- pip

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/MuziSan07/SairowSolutionsInovice-Generator.git
cd SairowSolutionsInovice-Generator

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets (see Configuration below)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## Configuration

Company contact details and payment accounts are read from
`.streamlit/secrets.toml` (which is git-ignored), then from environment
variables, and finally from built-in defaults. Copy
`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your
values.

Payment accounts are defined as repeated tables:

```toml
[[payment_accounts]]
account_holder = "Full Name"
method = "Easypaisa"
details = "03000000000"

[[payment_accounts]]
account_holder = "Full Name"
method = "Meezan Bank"
details = "IBAN: PK00XXXX0000000000000000"
```

If no payment accounts are configured, the payment-information table is omitted
from the generated invoice.

---

## Security notes

- Payment account numbers and IBANs are **not** stored in source code. Configure
  them in `.streamlit/secrets.toml`, which is excluded from version control.
- Generated PDFs are git-ignored so client invoices are never committed.
- Review commit history before making the repository public: earlier commits may
  still contain values that were later moved to secrets.

---

## Usage

1. Fill in company information in the sidebar.
2. Enter the client's details.
3. Add one or more items with a description, quantity, and rate.
4. Set the discount and tax as needed.
5. Click **Generate Invoice PDF**, then **Download Invoice PDF**.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
